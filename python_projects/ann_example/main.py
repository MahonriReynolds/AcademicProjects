
# imports
import torch
import torch.nn
import matplotlib.pyplot as plt
import seaborn as sns


# get iris dataset and take a look at he first couple entries
iris_dataset = sns.load_dataset('iris')
print(iris_dataset.head())


# quick visualization
pairplot = sns.pairplot(iris_dataset, hue='species')
# plt.show()


# convert from pandas dataframe to torch tensor 
iris_tensor = torch.tensor(iris_dataset[iris_dataset.columns[0:4]].values).float()


# convert species to numberic value
iris_labels = torch.zeros(len(iris_tensor), dtype=torch.long)
iris_labels[iris_dataset.species=='setosa'] = 0 # redundant but makes the numbering cleared
iris_labels[iris_dataset.species=='versicolor'] = 1
iris_labels[iris_dataset.species=='virginica'] = 2

# quick look at labels
print(iris_labels)


# prep torch ann, loss func, and optimizer
iris_ann = torch.nn.Sequential(
    torch.nn.Linear(4, 64),  # input layer
    torch.nn.ReLU(),
    torch.nn.Linear(64, 64), # hidden layer
    torch.nn.ReLU(),
    torch.nn.Linear(64, 3)   # output layer
)
iris_loss_func = torch.nn.CrossEntropyLoss()
iris_optimizer = torch.optim.SGD(iris_ann.parameters(), lr=0.01)


# init run variables
num_epochs = 1000
losses = torch.zeros(num_epochs)
ongoing_accuracy = []


# train the model
for epoch in range(num_epochs):
    # forward pass
    y_hat = iris_ann(iris_tensor)
    
    # compute loss
    loss = iris_loss_func(y_hat, iris_labels)
    losses[epoch] = loss
    
    # back propagate 
    iris_optimizer.zero_grad()
    loss.backward()
    iris_optimizer.step()
    
    # compute accuracy
    matches = torch.argmax(y_hat, axis=1) == iris_labels
    matches_numeric = matches.float()
    accuracy_pct = 100 * torch.mean(matches_numeric)
    ongoing_accuracy.append(accuracy_pct)

# final forward pass
predictions = iris_ann(iris_tensor)


# check the model's accuracy after training
prediction_labels = torch.argmax(predictions, axis=1)
final_accuracy = 100 * torch.mean((prediction_labels == iris_labels).float())


# model performance visualization
print(f'Final accuracy: {final_accuracy:.3f}')
fig, ax = plt.subplots(1, 2, figsize=(13, 4))

ax[0].plot(losses.detach())
ax[0].set_ylabel('Loss')
ax[0].set_xlabel('Epoch')
ax[0].set_title('Loss per Epoch')

ax[1].plot(ongoing_accuracy)
ax[1].set_ylabel('Accuracy')
ax[1].set_xlabel('Epoch')
ax[1].set_title('Accuracy per Epoch')

plt.show()
