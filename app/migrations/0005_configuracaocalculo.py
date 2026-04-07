from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_parcela_aplicar_multa'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfiguracaoCalculo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('multa_percentual', models.DecimalField(decimal_places=4, default=0.02, max_digits=5)),
                ('juros_percentual_mensal', models.DecimalField(decimal_places=4, default=0.01, max_digits=5)),
                ('taxa_boleto', models.DecimalField(decimal_places=2, default=3.0, max_digits=10)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
