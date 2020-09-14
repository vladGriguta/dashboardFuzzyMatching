
def matchStrings(attributes):
    from fuzzywuzzy import fuzz, process
    import pandas as pd
    import os
    
    wordList,orig_series,match_series = attributes[0],attributes[1],attributes[2]

    """
    df = pd.DataFrame(match_series)
    df['orig_series'] = orig_series
    df.to_csv('matched_data.csv',index=None)

    return df
    """

    if os.path.exists('matched_data.csv'): os.remove('matched_data.csv')

    def replaceWords(s):
        for word in wordList:
            s = s.replace(word,'')
        return s

    orig_series = orig_series.apply(lambda x: replaceWords(str(x).lower()))
    match_series = match_series.apply(lambda x: replaceWords(str(x).lower()))

    matching_col = []
    similarity = []
    for i,elem in match_series.iteritems():
        ratio = process.extract( elem, orig_series, limit=1, scorer = fuzz.token_set_ratio)
        matching_col.append(ratio[0][0])
        similarity.append(ratio[0][1])

    df = pd.DataFrame(match_series)
    df['matching_col'] = pd.Series(matching_col)
    df['similarity'] = pd.Series(similarity)

    df.sort_values('similarity',inplace=True,ascending=False)
    df = df.reset_index(drop=True).reset_index()

    df.to_csv('matched_data.csv',index=None)

    return True
    