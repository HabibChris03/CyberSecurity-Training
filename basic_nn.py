import numpy as np

# 1. Activation Function (Sigmoid) and its Derivative
def sigmoid(x):
    """
    Sigmoid function maps any value to a probability between 0 and 1.
    Formula: f(x) = 1 / (1 + e^-x)
    """
    return 1 / (1 + np.exp(-x))

def sigmoid_derivative(x):
    """
    Derivative of the sigmoid function, used during backpropagation.
    Formula: f'(x) = f(x) * (1 - f(x))
    """
    return x * (1 - x)

# 2. Define the training dataset (XOR Logic Gate)
# Input features: [Input 1, Input 2]
X = np.array([
    [0, 0],
    [0, 1],
    [1, 0],
    [1, 1]
])

# Expected target output: Output is 1 if inputs are different, 0 if they are the same
y = np.array([
    [0],
    [1],
    [1],
    [0]
])

# Set a random seed so results are reproducible
np.random.seed(42)

# 3. Neural Network Architecture Configuration
# We will build a 2-layer Neural Network:
# Input Layer (2 neurons) -> Hidden Layer (3 neurons) -> Output Layer (1 neuron)
input_size = 2
hidden_size = 3
output_size = 1

# Initialize Weights and Biases with small random values
# Weights connect neurons from one layer to the next
# Biases are added to the neuron inputs, similar to the constant (y-intercept) in linear equations
W1 = np.random.uniform(size=(input_size, hidden_size))
b1 = np.zeros((1, hidden_size))

W2 = np.random.uniform(size=(hidden_size, output_size))
b2 = np.zeros((1, output_size))

# Hyperparameters
learning_rate = 0.5
epochs = 10000  # Number of times the model will see the entire dataset during training

print("--- Training Started ---")

# 4. The Training Loop
for epoch in range(epochs):
    # --- FORWARD PROPAGATION ---
    # Step 1: Calculate activations for the hidden layer
    # z1 = X * W1 + b1
    hidden_layer_input = np.dot(X, W1) + b1
    hidden_layer_output = sigmoid(hidden_layer_input)
    
    # Step 2: Calculate activations for the output layer
    # z2 = hidden_output * W2 + b2
    output_layer_input = np.dot(hidden_layer_output, W2) + b2
    predicted_output = sigmoid(output_layer_input)
    
    # --- ERROR CALCULATION ---
    # Loss: How far off is our prediction from the actual target? (Using Mean Squared Error derivative)
    error = y - predicted_output
    
    # Print progress every 1,000 epochs
    if epoch % 1000 == 0:
        loss = np.mean(np.square(error))
        print(f"Epoch {epoch:5d} | Loss (MSE): {loss:.6f}")
        
    # --- BACKPROPAGATION (LEARNING) ---
    # We calculate how much each weight and bias contributed to the error
    # using the Chain Rule of calculus.
    
    # 1. Calculate the gradient/delta at the output layer
    # delta2 = error * derivative of sigmoid at output activation
    d_predicted_output = error * sigmoid_derivative(predicted_output)
    
    # 2. Calculate the error contribution of the hidden layer
    # how much did hidden neurons contribute to output errors?
    error_hidden_layer = d_predicted_output.dot(W2.T)
    
    # 3. Calculate the gradient/delta at the hidden layer
    d_hidden_layer = error_hidden_layer * sigmoid_derivative(hidden_layer_output)
    
    # --- PARAMETER UPDATES ---
    # Adjust weights and biases in the opposite direction of the gradient
    W2 += hidden_layer_output.T.dot(d_predicted_output) * learning_rate
    b2 += np.sum(d_predicted_output, axis=0, keepdims=True) * learning_rate
    
    W1 += X.T.dot(d_hidden_layer) * learning_rate
    b1 += np.sum(d_hidden_layer, axis=0, keepdims=True) * learning_rate

print("--- Training Finished ---\n")

# 5. Evaluate the Trained Model
print("--- Final Predictions ---")
# Run one final forward pass to see the predictions after training
final_hidden = sigmoid(np.dot(X, W1) + b1)
final_predictions = sigmoid(np.dot(final_hidden, W2) + b2)

for i in range(len(X)):
    print(f"Input: {X[i]} | Expected: {y[i][0]} | Predicted: {final_predictions[i][0]:.4f} (Round: {round(final_predictions[i][0])})")
