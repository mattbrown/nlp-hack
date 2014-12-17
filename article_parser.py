__author__ = 'mbrown'

import foxnewsscraper
import nlp_fun
import string


def do_analysis():
    """
    Table definition
    CREATE TABLE `analysis` (
      `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
      `subject` character varying(200),
      `sentiment` double,
      `subject_sentiment` double,
      `subjectivity` double,
      `title_subjectivity` double,
      `story_id` int(11) unsigned not null,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

     CREATE TABLE `stocknews_newscontent` (
      `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
      `url` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
      `title` varchar(4000) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
      `content` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
      `date` date DEFAULT NULL,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=279 DEFAULT CHARSET=utf8mb4;
    """
    cnx = foxnewsscraper.connect_to_db()
    cursor = cnx.cursor()

    query = "SELECT id, title, content FROM stocknews_newscontent"

    cursor.execute(query)

    for (id, title, content) in cursor:
        subject = classify(title)
        clean_title = nlp_fun.remove_stop_words(title)
        title_pol, title_sub = nlp_fun.score_feels(clean_title)

        clean_content = nlp_fun.remove_stop_words(content)
        content_pol, content_sub = nlp_fun.score_feels(clean_content)
        write_to_analysis_db(id, subject, content_pol, content_sub, title_pol, title_sub)
        # print "title: p %f s %f article p %f s %f ::: %s" % (title_pol, title_sub, content_pol, content_sub, title)

    cursor.close()
    cnx.close()


def write_to_analysis_db(article_id, subject, content_sentiment, content_subjectivity, title_sentiment, title_subjectivity):
    cnx = foxnewsscraper.connect_to_db()
    insert_cursor = cnx.cursor(prepared=True)
    insert_stmt = "INSERT INTO analysis (subject, sentiment, subject_sentiment, subjectivity, title_subjectivity, story_id) " \
                  "values (%s, %s, %s, %s, %s, %s);"
    insert_cursor.execute(insert_stmt, (subject, content_sentiment, title_sentiment, content_subjectivity, title_subjectivity, article_id))

    cnx.commit()
    cnx.close()

def classify(title):
    """
    We want to classify something as D, R, or None
    Democrat:
    Democrat,
    """
    democrat_words = ['democrat', 'dems', 'obama', 'liberal', 'progressive', 'left', 'warren', 'reid', 'pelosi', 'dnc', 'liberals', "obama's", 'obamas', 'hillary', 'dem', 'whitehouse']
    republican_words = ['republican', 'conservative', 'boehner', 'cruz', 'mcconnell', 'right', 'tea party', 'gop', 'bush', 'republicans']

    prepared_title = title.lower().replace('white house', 'whitehouse')

    is_democrat = False
    is_republican = False
    for word in prepared_title.split(' '):
        prepped_word = prepare_for_comparison(word)
        is_democrat = is_democrat or prepped_word in democrat_words
        is_republican = is_republican or prepped_word in republican_words

    classification = None
    if is_democrat and is_republican:
        classification = 'DR'
    elif is_democrat:
        classification = 'D'
    elif is_republican:
        classification = 'R'

    return classification

def prepare_for_comparison(word):
    #Remove puncuation because it won't be needed for compare
    exclude = set(string.punctuation)
    s = ''.join(ch for ch in word if ch not in exclude)
    return s


if __name__ == '__main__':
    do_analysis()