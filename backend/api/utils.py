def create_report(recipe_ingredients, file_name):
    with open(file_name, 'w') as file:
        for ing in recipe_ingredients:
            file.write(ing['ingredient__name'] + ' ' + str(ing['amount']))
