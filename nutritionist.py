from recipes import Forecast, NutritionFacts, SimilarRecipes
list_of_ingredients = input('Введите список ингредиентов на английском через запятую: ')
fr = Forecast(list_of_ingredients)
nf = NutritionFacts(list_of_ingredients)
sr = SimilarRecipes(list_of_ingredients)
if len(fr.unknown_ingredients) > 0:
        print("Неизвестные ингредиенты:")
        print(*fr.unknown_ingredients)
        print("Проанализируем только известные нам ингредиенты:")
        print(*fr.known_ingredients)
if len(fr.known_ingredients) == 0:
        print("Извините, но все введенные ингредиенты нам не известны.")
else:
        print("I. НАШ ПРОГНОЗ:")
        print(fr.predict_rating_category()[1])
        print()
        print('II. ПИЩЕВАЯ ЦЕННОСТЬ, ТОП-5 НУТРИЕНТОВ:')
        print(nf.filter(5))
        print()
        print('III. ТОП-3 ПОХОЖИХ РЕЦЕПТА:')
        if (sr.top_similar(3) is None) or (sr.top_similar(3) == ''):
            print("Похожих рецептов не найдено.")
        else:
            print(sr.top_similar(3))