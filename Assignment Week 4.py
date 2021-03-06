def blight_model():
    import pandas as pd
    import numpy as np
    from sklearn.preprocessing import LabelEncoder

    train_data = pd.read_csv("train.csv", encoding = 'ISO-8859-1')
    test_data = pd.read_csv("test.csv")
    address_data = pd.read_csv("addresses.csv")
    latlons_data = pd.read_csv("latlons.csv")
    
    # Cheking how our data looks like
    print(train_data.shape)
    train_data.head()
    
    print(test_data.shape)
    test_data.head()
    
    print(address_data.shape)
    address_data.head()
    
    print(latlons_data.shape)
    latlons_data.head()
    
    # Setting up the compliance variable
    train_data = train_data[(train_data['compliance'] == 0) | (train_data['compliance'] == 1)]
    
    # Joining the address and lat,lon data
    address_data = pd.merge(address_data, latlons_data, on = "address")
    
    # Mergning the train and test dataset with address, lat, lon
    train_data = pd.merge(train_data, address_data, on = "ticket_id")
    test_data = pd.merge(test_data, address_data, on = "ticket_id")
    
    # Lets see how our training data now looks like
    train_data.head()
    
    # Dropping the less important columns form train and test dataset
    train_data.drop(['agency_name', 'inspector_name', 'violator_name', 'non_us_str_code', 'violation_description', 
                'grafitti_status', 'state_fee', 'admin_fee', 'ticket_issued_date', 'hearing_date',
                # columns not available in test
                'payment_amount', 'balance_due', 'payment_date', 'payment_status', 
                'collection_status', 'compliance_detail', 
                # address related columns
                'violation_zip_code', 'country', 'address', 'violation_street_number',
                'violation_street_name', 'mailing_address_str_number', 'mailing_address_str_name', 
                'city', 'state', 'zip_code', 'address'], axis=1, inplace=True)
    test_data.drop(['agency_name', 'inspector_name', 'violator_name', 'non_us_str_code', 'violation_description', 
                'grafitti_status', 'state_fee', 'admin_fee', 'ticket_issued_date', 'hearing_date',
               'violation_zip_code', 'country', 'address', 'violation_street_number',
                'violation_street_name', 'mailing_address_str_number', 'mailing_address_str_name', 
                'city', 'state', 'zip_code', 'address'], axis = 1, inplace = True)
    
    # Let's check the training and testing sample data
    print(train_data.shape)
    print(test_data.shape)
    train_data.head()
    
    # DATA ANALYSIS
    # Converting disposition form string to numbers
    label_encoder = LabelEncoder()
    label_encoder.fit(train_data['disposition'].append(test_data['disposition'], ignore_index=True))
    train_data['disposition'] = label_encoder.transform(train_data['disposition'])
    test_data['disposition'] = label_encoder.transform(test_data['disposition'])
    
    # Converting violation_code from string to number
    label_encoder = LabelEncoder()
    label_encoder.fit(train_data['violation_code'].append(test_data['violation_code'], ignore_index=True))
    train_data['violation_code'] = label_encoder.transform(train_data['violation_code'])
    test_data['violation_code'] = label_encoder.transform(test_data['violation_code'])
    
    # Basic summary statistics of our training data
    train_data.describe(include = "all")
    
    # Checking for Null values in train dataset
    pd.isnull(train_data).sum()
    
    # Dropping Null values
    train_data.dropna(subset = ["lat", "lon"], axis = 0, inplace = True)
    
    # Checking for Null values in test dataset
    pd.isnull(test_data).sum()
    
    # Replacing Null Values
    test_data['lat'] = test_data['lat'].fillna(test_data['lat'].mean())
    test_data['lon'] = test_data['lon'].fillna(test_data['lon'].mean())
    
    # EXPLORATORY DATA ANALYSIS
    # Checking for correlation using correlation plot
    corr = train_data.corr()
    corr.style.background_gradient(cmap = "coolwarm")
    
    # From the above plot we can see that there is not much correlation between target variable i.e. compliance and other feature
    # Now we will use our train_data and split it into training and testing data and use our test_data for validation
    
    # Splitting our training dataset into train and test sets
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(train_data.ix[:,train_data.columns != "compliance"], 
                                                        train_data["compliance"],random_state = 0)
    
    # Lets check the no. of data elements in our new train and test sets
    print(X_train.shape)
    print(y_train.shape)
    print(X_test.shape)
    print(y_test.shape)
    
    # Using the Logistic Regression Model
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score

    lg = LogisticRegression()
    lg.fit(X_train, y_train)
    y1_predicted = lg.predict(X_test)
    lg_score_train = lg.score(X_train, y_train)
    lg_score_test = lg.score(X_test, y_test)
    print(y1_predicted)
    print("Training set score", lg_score_train)  # 0.92761950829
    print("Testing set score",lg_score_test)     # 0.926569927446
    
    # Getting the predicted probability scores
    y1_scores = lg.predict_proba(X_test)
    y1_scores = y1_scores[:,1]
    print(y1_scores)
    # Area under curve
    print("Test set AUC:", roc_auc_score(y_test, y1_scores))  # 0.755890845396
    
    # Building a Random Forets Model
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import GridSearchCV

    rf = RandomForestClassifier(random_state = 0)
    grid_values = {'n_estimators': [10, 100], 'max_depth': [None, 30]}
    grid_rf_auc = GridSearchCV(rf, param_grid = grid_values, scoring = "roc_auc")
    grid_rf_auc.fit(X_train, y_train)
    print("Best parameters:", grid_rf_auc.best_params_)  # 'max_depth': 30, 'n_estimators': 100
    print("Grid best AUC:", grid_rf_auc.best_score_)     # 0.809419694139
     
    return pd.DataFrame(grid_rf_auc.predict_proba(test_data)[:,1], test_data.ticket_id)

blight_model()

###################################################################
Area Under Curve Recieved 0.775319073943
    
