# Generated by Django 3.2 on 2023-07-03 15:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20230703_1810'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='usershoppingcart',
            name='unique_shopping_cart',
        ),
        migrations.RemoveField(
            model_name='usershoppingcart',
            name='favorite',
        ),
        migrations.AddField(
            model_name='usershoppingcart',
            name='recipe',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart', to='recipes.recipe'),
        ),
        migrations.AlterField(
            model_name='favorite',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite', to='recipes.recipe'),
        ),
        migrations.AddConstraint(
            model_name='usershoppingcart',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_shopping_cart'),
        ),
    ]
