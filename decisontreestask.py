# -*- coding: utf-8 -*-
"""DecisonTreesTask.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/18VDxAACvnEBK1UcECbl7dKtfR0FKuGOa
"""

beverage_data = [
    [12.0, 1.5, 1, 'Wine'],
    [5.0, 2.0, 0, 'Beer'],
    [40.0, 0.0, 1, 'Whiskey'],
    [13.5, 1.2, 1, 'Wine'],
    [4.5, 1.8, 0, 'Beer'],
    [38.0, 0.1, 1, 'Whiskey'],
    [11.5, 1.7, 1, 'Wine'],
    [5.5, 2.3, 0, 'Beer']
]

# Convert labels to integers
category_map = {'Wine': 0, 'Beer': 1, 'Whiskey': 2}
reverse_category_map = {v: k for k, v in category_map.items()}

# Create feature and target arrays
features = np.array([[entry[0], entry[1], entry[2]] for entry in beverage_data])
targets = np.array([category_map[entry[3]] for entry in beverage_data])

class TreeNode:
    def __init__(self, split_feature=None, split_value=None, left_child=None, right_child=None, prediction=None):
        self.split_feature = split_feature
        self.split_value = split_value
        self.left_child = left_child
        self.right_child = right_child
        self.prediction = prediction  # For leaf nodes: class label

class BeverageClassifier:
    def __init__(self, max_levels=3, min_split_size=2, split_metric='gini'):
        self.max_levels = max_levels
        self.min_split_size = min_split_size
        self.split_metric = split_metric
        self.tree_root = None
        self.attribute_names = ['AlcoholLevel', 'SugarLevel', 'Shade']

    def train(self, features, targets):
        self.tree_root = self._build_tree(features, targets, level=0)

    def _gini_index(self, targets):
        frequencies = np.bincount(targets)
        probs = frequencies / len(targets)
        return 1 - np.sum(probs ** 2)

    def _entropy_measure(self, targets):
        frequencies = np.bincount(targets)
        probs = frequencies / len(targets)
        probs = probs[probs > 0]
        return -np.sum(probs * np.log2(probs))

    def _purity(self, targets):
        return self._gini_index(targets) if self.split_metric == 'gini' else self._entropy_measure(targets)

    def _optimal_split(self, features, targets):
        num_samples, num_attributes = features.shape
        highest_gain = -np.inf
        optimal_feature, optimal_threshold = None, None

        base_purity = self._purity(targets)

        for attribute in range(num_attributes):
            thresholds = np.unique(features[:, attribute])
            for threshold in thresholds:
                left_mask = features[:, attribute] <= threshold
                right_mask = ~left_mask

                if sum(left_mask) < self.min_split_size or sum(right_mask) < self.min_split_size:
                    continue

                left_purity = self._purity(targets[left_mask])
                right_purity = self._purity(targets[right_mask])

                weighted_purity = (sum(left_mask) * left_purity + sum(right_mask) * right_purity) / num_samples
                split_gain = base_purity - weighted_purity

                if split_gain > highest_gain:
                    highest_gain = split_gain
                    optimal_feature = attribute
                    optimal_threshold = threshold

        return optimal_feature, optimal_threshold

    def _build_tree(self, features, targets, level):
        sample_count = len(targets)
        unique_classes = len(np.unique(targets))

        # Stopping criteria
        if (level >= self.max_levels or unique_classes == 1 or sample_count < self.min_split_size):
            return TreeNode(prediction=np.bincount(targets).argmax())

        # Find best split
        attribute, threshold = self._optimal_split(features, targets)
        if attribute is None:
            return TreeNode(prediction=np.bincount(targets).argmax())

        # Split data
        left_mask = features[:, attribute] <= threshold
        right_mask = ~left_mask

        # Recursively build children
        left_child = self._build_tree(features[left_mask], targets[left_mask], level + 1)
        right_child = self._build_tree(features[right_mask], targets[right_mask], level + 1)

        return TreeNode(attribute, threshold, left_child, right_child)

    def classify(self, features):
        return np.array([self._navigate_tree(sample, self.tree_root) for sample in features])

    def _navigate_tree(self, sample, node):
        if node.prediction is not None:
            return node.prediction
        if sample[node.split_feature] <= node.split_value:
            return self._navigate_tree(sample, node.left_child)
        return self._navigate_tree(sample, node.right_child)

    def display_tree(self, node=None, level=0):
        if node is None:
            node = self.tree_root
        indent = "  " * level
        if node.prediction is not None:
            print(f"{indent}Predict: {reverse_category_map[node.prediction]}")
        else:
            print(f"{indent}{self.attribute_names[node.split_feature]} <= {node.split_value:.2f}")
            print(f"{indent}Left:")
            self.display_tree(node.left_child, level + 1)
            print(f"{indent}Right:")
            self.display_tree(node.right_child, level + 1)

    def plot_boundaries(self, features, targets):
        x_lower, x_upper = features[:, 0].min() - 1, features[:, 0].max() + 1
        y_lower, y_upper = features[:, 1].min() - 1, features[:, 1].max() + 1
        grid_x, grid_y = np.meshgrid(np.arange(x_lower, x_upper, 0.1), np.arange(y_lower, y_upper, 0.1))

        # Predict for shade=0 and shade=1 separately
        preds_0 = self.classify(np.c_[grid_x.ravel(), grid_y.ravel(), np.zeros(grid_x.size)])
        preds_1 = self.classify(np.c_[grid_x.ravel(), grid_y.ravel(), np.ones(grid_x.size)])

        preds_0 = preds_0.reshape(grid_x.shape)
        preds_1 = preds_1.reshape(grid_x.shape)

        fig, (plot1, plot2) = plt.subplots(1, 2, figsize=(12, 5))

        # Shade = 0
        plot1.contourf(grid_x, grid_y, preds_0, alpha=0.4, cmap='viridis')
        scatter = plot1.scatter(features[:, 0], features[:, 1], c=targets, cmap='viridis', edgecolor='k')
        plot1.set_title('Decision Boundary (Shade=0)')
        plot1.set_xlabel('Alcohol Content (%)')
        plot1.set_ylabel('Sugar Content (g/L)')
        plot1.legend(handles=scatter.legend_elements()[0], labels=['Wine', 'Beer', 'Whiskey'])

        # Shade = 1
        plot2.contourf(grid_x, grid_y, preds_1, alpha=0.4, cmap='viridis')
        plot2.scatter(features[:, 0], features[:, 1], c=targets, cmap='viridis', edgecolor='k')
        plot2.set_title('Decision Boundary (Shade=1)')
        plot2.set_xlabel('Alcohol Content (%)')
        plot2.set_ylabel('Sugar Content (g/L)')

        plt.tight_layout()
        plt.show()

# Step 6: Evaluation
evaluation_data = np.array([
    [6.0, 2.1, 0],   # Expected: Beer
    [39.0, 0.05, 1], # Expected: Whiskey
    [13.0, 1.3, 1]   # Expected: Wine
])

# Train and evaluate with Gini
print("Training Decision Tree with Gini criterion...")
gini_model = BeverageClassifier(max_levels=3, min_split_size=2, split_metric='gini')
gini_model.train(features, targets)
gini_predictions = gini_model.classify(evaluation_data)
print("\nTree Structure (Gini):")
gini_model.display_tree()
print("\nPredictions (Gini):")
for i, pred in enumerate(gini_predictions):
    print(f"Test {i+1}: Predicted {reverse_category_map[pred]}, Expected {reverse_category_map[[1, 2, 0][i]]}")
gini_model.plot_boundaries(features, targets)

# Train and evaluate with Entropy
print("\nTraining Decision Tree with Entropy criterion...")
entropy_model = BeverageClassifier(max_levels=3, min_split_size=2, split_metric='entropy')
entropy_model.train(features, targets)
entropy_predictions = entropy_model.classify(evaluation_data)
print("\nTree Structure (Entropy):")
entropy_model.display_tree()
print("\nPredictions (Entropy):")
for i, pred in enumerate(entropy_predictions):
    print(f"Test {i+1}: Predicted {reverse_category_map[pred]}, Expected {reverse_category_map[[1, 2, 0][i amendments to variable names and method names while preserving the exact functionality. The changes include: