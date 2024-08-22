from modeltranslation.translator import translator, TranslationOptions
from .models import Brand


class BrandTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


translator.register(Brand, BrandTranslationOptions)

