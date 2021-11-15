import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from keras.models import Sequential
from keras.layers import Dense
from keras import regularizers
import pydot
from IPython.display import SVG
from keras.utils.vis_utils import model_to_dot
from keras.models import load_model



data = pd.read_csv('Model_Build/data/final_dataset.csv')
first = list(range(1,40))
second = list(range(41,107))
first = first + second + [209]
data = data.iloc[:, first]
x, y = data.iloc[:, 4:(data.shape[1]-1)], data.iloc[:, (data.shape[1]-1)]
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = 0)
scaler = StandardScaler()
x_train_scaled = scaler.fit_transform(x_train)
x_test_scaled = scaler.transform(x_test)



model = Sequential()
model.add(Dense(16, input_dim=x_train_scaled.shape[1],
                activation='relu', kernel_regularizer=regularizers.l2(0.01)))
model.add(Dense(32, activation='relu', kernel_regularizer=regularizers.l2(0.01)))
model.add(Dense(32, activation='relu', kernel_regularizer=regularizers.l2(0.01)))
model.add(Dense(16, activation='relu', kernel_regularizer=regularizers.l2(0.01)))
model.add(Dense(16, activation='relu', kernel_regularizer=regularizers.l2(0.01)))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='Adam', metrics=['accuracy'])




model.fit(x=x_train_scaled, y=y_train, epochs=200, batch_size=64, verbose=0)
test_results = model.evaluate(x = x_test_scaled, y = y_test, verbose=0)
print("Test Accuracy = {}".format(test_results[1]))



model.save('dl_model.h5')
# loaded_model = load_model('Model_Build/dl_model.h5')