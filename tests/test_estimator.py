from S3EN.estimator import s3enEstimator
import numpy as np
from sklearn.preprocessing import LabelEncoder
import pandas as pd

df = pd.read_csv('train.csv')
good_feats_df = df[['Fare',
                    'SibSp',
                    'Cabin',
                    'Pclass',
                    'Sex',
                    'Parch',
                    'Embarked',
                    'Age']]

feature_list = []
data_types = good_feats_df.dtypes
le = LabelEncoder()
for i, column in enumerate(data_types.index):
    feature_dict = {}
    feature_dict['feat_nm'] = column
    if data_types[i] == 'object':
        feature_dict['type'] = 'categorical'
        input_dim = good_feats_df[column].nunique()
        output_dim = max(int(np.sqrt(input_dim-1)), 1)
        feature_dict['input_dim'] = input_dim
        feature_dict['output_dim'] = output_dim
        good_feats_df[column] = good_feats_df[column].fillna('NaN')
        good_feats_df[column] = le.fit_transform(good_feats_df[column])
    else:
        good_feats_df[column] = good_feats_df[column].fillna(0).astype(float)
        feature_dict['type'] = 'numerical'
    feature_list.append(feature_dict)

X = good_feats_df
y = df['Survived'].values

def test_shape():
    model = s3enEstimator(feature_list=feature_list,
                          target_type='classification',
                          validation_ratio=0,
                          patience=3,
                          nb_models_per_stack=2,
                          nb_variables_per_model=2,
                          nb_stack_blocks=2,
                          width=1,
                          depth=1,
                          epochs=1
                          )
    model.fit(X, y)
    predictions = model.predict(X)
    assert len(y) == len(predictions)

def test_classifier_accuracy():
    model = s3enEstimator(feature_list=feature_list,
                          target_type='classification',
                          validation_ratio=0,
                          patience=None,
                          nb_models_per_stack=10,
                          nb_variables_per_model=4,
                          nb_stack_blocks=20,
                          width=1,
                          depth=1,
                          epochs=300,
                          batch_norm='no',
                          dropout_rate=0
                          )
    model.fit(X, y)
    assert np.mean((model.predict(X) > 0.5).astype(float) == y) >= 0.75

def test_classifier_accuracy_patience():
    model = s3enEstimator(feature_list=feature_list,
                          target_type='classification',
                          validation_ratio=0.1,
                          patience=5,
                          nb_models_per_stack=10,
                          nb_variables_per_model=4,
                          nb_stack_blocks=20,
                          width=1,
                          depth=1,
                          epochs=1000,
                          batch_norm='no',
                          dropout_rate=0
                          )
    model.fit(X, y)
    assert np.mean((model.predict(X) > 0.5).astype(float) == y) >= 0.75

def test_classifier_accuracy_dropout_batchnorm():
    model = s3enEstimator(feature_list=feature_list,
                          target_type='classification',
                          validation_ratio=0.2,
                          patience=5,
                          nb_models_per_stack=10,
                          nb_variables_per_model=4,
                          nb_stack_blocks=20,
                          width=3,
                          depth=1,
                          epochs=2000,
                          batch_norm='yes',
                          dropout_rate=0.1
                          )
    model.fit(X, y)
    assert np.mean((model.predict(X) > 0.5).astype(float) == y) >= 0.75

def test_classifier_accuracy_using_regression():
    model = s3enEstimator(feature_list,
                          target_type='regression',
                          validation_ratio=0,
                          patience=3,
                          nb_models_per_stack=10,
                          nb_variables_per_model=4,
                          nb_stack_blocks=20,
                          width=1,
                          depth=1,
                          epochs=1000,
                          batch_norm='no',
                          dropout_rate=0
                          )
    model.fit(X, y)
    assert np.mean((model.predict(X) > 0.5).astype(float) == y) >= 0.75

def test_classifier_accuracy_using_regression_batchnorm_dropout():
    model = s3enEstimator(feature_list,
                          target_type='regression',
                          validation_ratio=0,
                          patience=3,
                          nb_models_per_stack=10,
                          nb_variables_per_model=5,
                          nb_stack_blocks=20,
                          width=2,
                          depth=1,
                          epochs=2000,
                          batch_norm='yes',
                          dropout_rate=0.2
                          )
    model.fit(X, y)
    assert np.mean((model.predict(X) > 0.5).astype(float) == y) >= 0.75

def test_random_gridSearch_classifier():
    from sklearn.model_selection import RandomizedSearchCV
    grid = {
        'width': [2, 1]
    }
    model = s3enEstimator(feature_list,
                          target_type='classification',
                          validation_ratio=0,
                          patience=None,
                          nb_models_per_stack=2,
                          nb_variables_per_model=2,
                          nb_stack_blocks=2,
                          width=1,
                          depth=1,
                          epochs=1
                          )
    rgs = RandomizedSearchCV(model, grid, n_iter=2, random_state=0)
    rgs.fit(X, y)
    assert True #no error returned