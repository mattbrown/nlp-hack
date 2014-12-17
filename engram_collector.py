__author__ = 'mbrown'

import nlp_fun
import foxnewsscraper

def remove_empty_and_weird_character(article_text_list):
    lala = [word for word in article_text_list if word not in ['', u'\u2013']]
    return lala

def gather_engrams():
    all_text =  get_all_article_text()
    clean_all_text = nlp_fun.remove_stop_words(all_text)
    clean_all_text = remove_empty_and_weird_character(clean_all_text)

    print "Common Words"
    for word in nlp_fun.common_words(clean_all_text):
        print word

    print "Bigrams"
    print nlp_fun.find_bigrams(clean_all_text)

    print "Bigrams with span"
    nlp_fun.find_bigrams_span(clean_all_text, 5)


def get_all_article_text():
    cnx = foxnewsscraper.connect_to_db()
    cursor = cnx.cursor()

    query = "SELECT id, title, content FROM stocknews_newscontent"

    cursor.execute(query)
    article_text = []

    for (id, title, content) in cursor:
        article_text.append(content)

    cursor.close()
    cnx.close()

    return "\n".join(article_text)



if __name__ == "__main__":
    gather_engrams()
