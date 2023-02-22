import numpy as np
import pandas as pd
from joblib import load
import warnings

warnings.filterwarnings("ignore")


class Forecast:
#Предсказание рейтинга блюда или его класса
    def __init__(self, list_of_ingredients):
        all_ingredients = pd.read_csv('nutrients.csv').drop(columns=['nutrient', 'value', 'nutrient_api']).columns
        self.list_of_ingredients = [ingredient.lower().strip() for ingredient in list_of_ingredients.split(',')]
        self.known_ingredients = []
        self.unknown_ingredients = []
        for ingredient in self.list_of_ingredients:
            if ingredient in all_ingredients:
                self.known_ingredients.append(ingredient)
            elif ingredient != '':
                self.unknown_ingredients.append(ingredient)

    def preprocess(self):
        #Этот метод преобразует список ингредиентов в структуры данных,
        #которые используются в алгоритмах машинного обучения, чтобы сделать предсказание.

        all_ingredients = pd.read_csv('nutrients.csv').drop(columns=['nutrient', 'value', 'nutrient_api']).columns
        vector = pd.DataFrame(data=[np.zeros(len(all_ingredients))], columns=all_ingredients)
        for ingredient in self.known_ingredients:
            vector.loc[0, [ingredient]] = 1.0
        return vector

    def predict_rating_category(self):
        #Этот метод возвращает рейтинг (плохое/нормальное/отличное сочетание) для списка ингредиентов,
        # используя модель классификации, которая была обучена заранее. Помимо самого рейтинга, метод
        # также возвращает текст, который дает интерпретацию этого рейтинга и рекомендацию.

        model = load('best_model.joblib')
        rating_category = model.predict(self.preprocess())[0]
        if rating_category == 'bad':
            text = 'Плохое сочетание ингредиентов. Возможно, вам и понравится, но мы бы не рекомендовали такое сочетание'
        elif rating_category == 'so-so':
            text = 'Среднее сочетание ингредиентов'
        else:
            text = 'Отличное сочетание ингредиентов.'
        return rating_category, text


class NutritionFacts:
#Выдает информацию о пищевой ценности ингредиентов.
    def __init__(self, list_of_ingredients):
        all_ingredients = pd.read_csv('nutrients.csv').drop(columns=['nutrient', 'value', 'nutrient_api']).columns
        self.list_of_ingredients = [ingredient.lower().strip() for ingredient in list_of_ingredients.split(',')]
        self.known_ingredients = []
        self.unknown_ingredients = []
        for ingredient in self.list_of_ingredients:
            if ingredient in all_ingredients:
                self.known_ingredients.append(ingredient)
            elif ingredient != '':
                self.unknown_ingredients.append(ingredient)

    def retrieve(self):
        #Этот метод получает всю имеющуюся информацию о пищевой ценности из файла с заранее собранной информацией
        # по заданным ингредиентам. Он возвращает ее в том виде, который вам кажется наиболее удобным и подходящим.

        facts = pd.read_csv('nutrients.csv')[['nutrient'] + self.known_ingredients]
        return facts

    def filter(self, n):
        #Этот метод отбирает из всей информации о пищевой ценности только те нутриенты, которые были
        #заданы в must_nutrients, а также топ-n нутриентов с наибольшим значением дневной нормы
        #потребления для заданного ингредиента.

        text_with_facts = ''
        for ingredient in self.known_ingredients:
            text_with_facts += f'{ingredient.title()}\n'
            top_n_nutrients = self.retrieve()[['nutrient', ingredient]].sort_values(ingredient, ascending=False).head(n)
            for index, row in top_n_nutrients.iterrows():
                text_with_facts += f'{row["nutrient"]} - {round(row[ingredient])}% of Daily Value\n'
            text_with_facts += '\n'
        return text_with_facts


class SimilarRecipes:
#Рекомендация похожих рецептов с дополнительной информацией
    def __init__(self, list_of_ingredients):
        all_ingredients = pd.read_csv('nutrients.csv').drop(columns=['nutrient', 'value', 'nutrient_api']).columns
        self.list_of_ingredients = [ingredient.lower().strip() for ingredient in list_of_ingredients.split(',')]
        self.known_ingredients = []
        self.unknown_ingredients = []
        for ingredient in self.list_of_ingredients:
            if ingredient in all_ingredients:
                self.known_ingredients.append(ingredient)
            elif ingredient != '':
                self.unknown_ingredients.append(ingredient)

    def find_all(self):
        #Этот метод возвращает список индексов рецептов, которые содержат заданный список ингредиентов. Если нет
        # ни одного рецепта, содержащего все эти ингредиенты, то сделайте обработку ошибки, чтобы программа не ломалась.
        indexes = None
        recipes = pd.read_csv('recipes.csv')
        for ingredient in self.known_ingredients:
            recipes = recipes[recipes[ingredient] == 1.0]
            if len(recipes) == 0:
                return indexes
        indexes = recipes.index
        return indexes

    def top_similar(self, n):
        #Этот метод возвращает текст с заголовком, рейтингом и URL.
        # Чтобы это сделать, он вначале находит топ-n наиболее похожих рецептов с точки зрения количества
        # дополнительных ингредиентов, которые потребуются в этих рецептах. Наиболее похожим будет тот, в котором
        # не требуется никаких других ингредиентов. Далее идет тот, у которого появляется 1 доп. ингредиент.
        # Далее – 2. Если рецепт нуждается в более, чем 5 доп. ингредиентах, то такой рецепт не выводится.
        text_with_recipes = None
        try:
            similar_recipes = pd.read_csv('recipes.csv').iloc[self.find_all()]
        except:
            return text_with_recipes
        if n <= 0:
            return text_with_recipes
        similar_recipes['count_ingredients'] = similar_recipes[similar_recipes.columns[9:-1]].apply(sum, axis=1)
        similar_recipes = similar_recipes[similar_recipes['count_ingredients'] < (5 + len(self.known_ingredients))]
        top_n_recipes = similar_recipes.sort_values('count_ingredients').head(n)
        text_with_recipes = ''
        for index, row in top_n_recipes.iterrows():
            text_with_recipes += f"- {row['title']}, рейтинг: {str(row['rating'])}, URL: {row['link']}\n"
        return text_with_recipes
