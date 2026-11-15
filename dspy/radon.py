from typing import Any

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

def plot_radon_theorem():
    fig = plt.figure(figsize=(10, 8))
    # mplot3d is untyped (e.g. zs is inferred as int), so don't type-check Axes3D calls.
    ax: Any = fig.add_subplot(111, projection='3d')

    # --- Define the Points ---
    # Set A: 3 points forming a triangle in the XY plane (z=0)
    # A1, A2, A3
    A = np.array([
        [1, 0, 0],   # A1
        [-0.5, np.sqrt(3)/2, 0], # A2
        [-0.5, -np.sqrt(3)/2, 0] # A3
    ])
    
    # Set B: 2 points forming a segment that passes through the origin
    # The origin (0,0,0) is the centroid of the triangle A.
    # We put B1 below and B2 above the center of the triangle.
    B = np.array([
        [0, 0, -1],  # B1
        [0, 0, 1]    # B2
    ])

    # --- Plot Set A (The Triangle) ---
    # Plot vertices
    ax.scatter(A[:,0], A[:,1], A[:,2], c='blue', s=100, label='Set A (Triangle)')
    
    # Plot edges of the triangle
    # Order: A1->A2->A3->A1
    triangle_indices = [0, 1, 2, 0]
    ax.plot(A[triangle_indices, 0], A[triangle_indices, 1], A[triangle_indices, 2], c='blue', alpha=0.6)

    # Add semi-transparent surface
    verts = [list(zip(A[:,0], A[:,1], A[:,2]))]
    poly = Poly3DCollection(verts, alpha=0.3, facecolors='cyan')
    ax.add_collection3d(poly)

    # --- Plot Set B (The Segment) ---
    # Plot vertices
    ax.scatter(B[:,0], B[:,1], B[:,2], c='red', s=100, label='Set B (Segment)')
    
    # Plot the segment B1-B2
    ax.plot(B[:,0], B[:,1], B[:,2], c='red', linewidth=3)

    # --- Plot the Intersection ---
    # In this setup, the intersection is exactly at the origin (0,0,0)
    ax.scatter([0], [0], [0], c='black', s=150, marker='x', label='Intersection')

    # --- Labels ---
    # Offset for labels to make them readable
    offset = 0.1
    
    # Label A points
    ax.text(A[0,0]+offset, A[0,1], A[0,2], '$A_1$', fontsize=12, color='blue')
    ax.text(A[1,0]+offset, A[1,1], A[1,2], '$A_2$', fontsize=12, color='blue')
    ax.text(A[2,0]+offset, A[2,1], A[2,2], '$A_3$', fontsize=12, color='blue')

    # Label B points
    ax.text(B[0,0], B[0,1], B[0,2]-offset, '$B_1$', fontsize=12, color='red')
    ax.text(B[1,0], B[1,1], B[1,2]+offset, '$B_2$', fontsize=12, color='red')

    # --- Formatting ---
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    
    # Remove axis numbers for a cleaner "diagram" look
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])

    # Title and Equation
    plt.title(r"Radon's Theorem in $\mathbb{R}^3$ (5 Points)", fontsize=16)
    
    # Add text for the sets and intersection equation
    plt.figtext(0.5, 0.05, 
                r"Set $A = \{A_1, A_2, A_3\}$ (Triangle)" + "\n" +
                r"Set $B = \{B_1, B_2\}$ (Segment)" + "\n\n" +
                r"$\text{conv}(A) \cap \text{conv}(B) \neq \emptyset$", 
                ha="center", fontsize=14, bbox={"facecolor":"orange", "alpha":0.1, "pad":5})

    plt.legend()
    plt.show()

if __name__ == "__main__":
    plot_radon_theorem()