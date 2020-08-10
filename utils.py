
def matchStrings(wordList,orig_series,match_series):
    import pandas as pd
    
    def replaceWords(s):
        for word in wordList:
            s = s.replace(word,'')
        return s

    orig_series = orig_series.apply(lambda x: replaceWords(str(x).lower()))
    match_series = match_series.apply(lambda x: replaceWords(str(x).lower()))

    matching_col = []
    similarity = []
    for i,elem in match_series.iterrows():
        ratio = process.extract( elem, orig_series, limit=1, scorer = fuzz.token_set_ratio)
        matching_col.append(ratio[0][0])
        similarity.append(ratio[0][1])

    df = pd.DataFrame(match_series)
    df['matching_col'] = pd.Series(matching_col)
    df['similarity'] = pd.Series(similarity)

    df.sort_values('similarity',inplace=True,ascending=False)
    df = df.reset_index(drop=True).reset_index()