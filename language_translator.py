
#chcp 65001
#Run in terminal

from googletrans import Translator

# create an instance of the Translator class
translator = Translator(service_urls=['translate.google.co.in'])

# English text to be translated
english_text = "kannada"

try:
    # translate the text to Kannada
    kannada_translation = translator.translate(text=english_text, dest='kn')

    # print the translated text
    print("English Text: ", english_text)
    print("Kannada Translation: ", kannada_translation.text.encode('utf-8').decode('utf-8'))

except Exception as e:
    print("Translation Error:", e)


