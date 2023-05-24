import nltk
import re
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from gensim import corpora, models
from CCPDict import Terms

#Sentiment analysis function
async def analyze_sentiment(message):
    
    # Prepare text
    text_content = message.content
    documents = [text_content]
    # Tokenize and remove stopwords
    stop_words = set(stopwords.words('english'))
    tokenized_documents = [word_tokenize(doc.lower()) for doc in documents]
    filtered_documents = [
        [word for word in doc if word not in stop_words]
        for doc in tokenized_documents
    ]

    # Create a dictionary
    dictionary = corpora.Dictionary(filtered_documents)

    # Create a corpus
    corpus = [dictionary.doc2bow(doc) for doc in filtered_documents]

    # Perform topic modeling
    num_topics = 3
    lda_model = models.LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=10)

    # Sentiment analysis
    sid = SentimentIntensityAnalyzer()

    for i, doc in enumerate(documents):
        # Sentiment analysis
        scores = sid.polarity_scores(doc)
        compound_score = scores['compound']

        # Topic modeling
        bow = dictionary.doc2bow(filtered_documents[i])
        topic_probabilities = lda_model.get_document_topics(bow)
        topic_probabilities.sort(key=lambda x: x[1], reverse=True)
        top_topic = topic_probabilities[0][0]

        matching_topics = []  # List to store the matched topics

        for topic_name, terms in Terms.items():
            for entry in terms:
                if abs(compound_score) > 0.5 and re.search(entry, doc) :
                    matching_topics.append(topic_name)
                    break

        if matching_topics:
            print("Document:", doc)
            print("Sentiment:", compound_score)
            print("Topics:", matching_topics)
            print("--------")
            return (
                {
                    'topic': matching_topics[0],
                    'compound score': compound_score
                }
            )
        else:
            return None
