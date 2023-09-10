import numpy as np
import matplotlib.pyplot as plt
from .Statistic_tools import auto_correlation
from typing import Callable, List
    



# def ESS(Thetas):

#     """
    
#     Calculating the Effective Sample Size(ESS) of the inputed data 

#     Arguments
#     ---------
#     thetas : the inputed value of the parameter theta generated by the stochastic precess

#     Returns
#     -------
#     res : the Effective Sample Szie of inputed data
    
#     """

#     Thetas =np.asarray(Thetas)
#     if len(Thetas.shape)==1:
#         Thetas = np.expand_dims(Thetas, axis=1)
#     # Computing the autocorrelation function
#     (m, n) = Thetas.shape
#     acf = np.asarray([auto_correlation(Thetas=Thetas, time_lag=t) for t in range(0, m)])
#     # Computing the integrated autocorrelation tine
#     iact = 1.0
#     for t in range(1, len(acf)):
#         for i in range(0, n):
#             if acf[t, i]<0:
#                 acf[:, i] = 0
#         iact += 2.0*acf[t]
#     return m/iact

def auto_corr_plot(Thetas, plot_nth_theta, theta_index, Threshold=0.2, max_time_lag=None, data_range=[], set_title="", plot_together=True, figsize=(10, 10), Saving_address=""):
    """
    
    plot the auto-correlation of each time_lag

    Arguments
    ---------
    Thetas (List[List[float]]): the value of the the parameters
    plot_nth_theta (List[int]): the dimensions want to plot with the function
    theta_index (List[]): the indexes of different dimension parameters
    Threshold (float): the threshold to mark a point on the graph
    step_width (int): the step width of the plot
    max_time_lag (int): the maximum time lag value to plot with the function
    data_range (List[int]) : the range of the data plotted by the function [t_min, t_max]
    plot_together (bool): deciding whether to plot all plots of auto-correlation together
    figsize : the figure size of the plots

    Returns
    -------
    None

    """

    Thetas = np.asarray(Thetas)
    if len(Thetas.shape)==1:
        Thetas = np.expand_dims(Thetas,axis=1)
    if not(data_range):
        data_range = [0, Thetas.shape[0]]
    if not(max_time_lag):
        max_time_lag = (data_range[1]-data_range[0])//30
    plt.rcParams["figure.figsize"] = figsize
    CrossPoint = []
    with plt.style.context("ggplot"):
        plt.axhline(y=Threshold, xmin=0, xmax=max_time_lag, linestyle="--")
        for i in plot_nth_theta:
            theta_i = Thetas[data_range[0]: data_range[1], i]
            m = theta_i.shape[0] # the data size of the plotted dataset
            acf = np.asarray([auto_correlation(Thetas=theta_i, time_lag=t)[0] for t in range(0, max_time_lag+1)])
            CrossPoints = np.where(acf<=Threshold)[0]
            cp = 0
            if (len(CrossPoints)>0):
                cp = CrossPoints[0]
            else:
                cp = "N/A"
            CrossPoint.append(cp)
            
            plt.plot(np.asarray(range(0, max_time_lag+1)), acf, label=f"The auto-correlation value of {theta_index[i]}, lower than {Threshold} at step {cp}")
            if not(plot_together):
                if (set_title):
                    plt.title(set_title)
                plt.legend()
                plt.xlabel("Time Lag Value")
                plt.ylabel("Auto-Correlation Value")
                plt.show()

        if plot_together:
            if (set_title):
                plt.title(set_title)
            plt.legend()
            plt.xlabel("Time Lag Value")
            plt.ylabel("Auto-Correlation Value")
            if (Saving_address):
                plt.savefig(Saving_address)
            plt.show()
    return CrossPoint

def targetDis_step_plot(Thetas, rho: Callable, target_type: str, burn_in=0, return_maximum=False, return_minimum=False, figsize=(6,8), Saving_address="", zoom_size=0, Convergence_Percentage=0.9):

    datasize = len(Thetas)
    steps = list(range(burn_in, datasize))
    target_vals = np.asarray([rho(theta) for theta in Thetas[burn_in:]])
    if return_maximum:
        max_step = np.argmax(target_vals)
    if return_minimum:
        min_step = np.argmin(target_vals)
        
    Convergence_val = np.mean(target_vals[int(datasize*(1-Convergence_Percentage)):])
    if (zoom_size):
        Convergence_min = np.min(target_vals[int(datasize*0.1):])
        SubC = np.where(target_vals>=Convergence_min)[0][0]
        SubXL = np.max([SubC - zoom_size, 0])
        SubXR = np.min([SubC + zoom_size, datasize])

    with plt.style.context("ggplot"):
        plt.rcParams["figure.figsize"] = figsize
        plt.axhline(Convergence_val, linestyle="--", alpha=0.6, color='b', label="The Convergence Line")
        plt.plot(
            steps, 
            target_vals,
            label="the "+target_type+" value of each step of iteration"
            )

        if return_maximum:
            plt.scatter([max_step], [target_vals[max_step]], c="black", label=f"the {max_step}th step maximize the "+target_type, zorder=2)
        if return_minimum:
            plt.scatter([min_step], [target_vals[min_step]], c="blue", label=f"the {min_step}th step minimize the "+target_type, zorder=2)
        
        if (zoom_size):
            # Create a set of inset Axes: these should fill the bounding box allocated to them.
            ax = plt.gca()
            axins = ax.inset_axes([0.5, 0.1, 0.47, 0.47])
            axins.plot(steps[SubXL: SubXR], target_vals[SubXL: SubXR])
            axins.axhline(Convergence_val, linestyle="--", alpha=0.6, color='b')

            # Set the axis limits
            x1, x2, y1, y2 = SubXL - zoom_size*0.1, SubXR + zoom_size*0.1, min(target_vals[SubXL: SubXR]), max(target_vals[SubXL: SubXR])*0.6
            axins.set_xlim(x1, x2)
            axins.set_ylim(y1, y2)
            
            # Make the tick labels of the right and top axes visible
            axins.xaxis.set_visible(True)
            axins.yaxis.set_visible(True)
            
            # draw a bbox of the region of the inset axes in the parent axes and
            # connecting lines between the bbox and the inset axes area
            ax.indicate_inset_zoom(axins, edgecolor="black")
        
        plt.legend(fontsize=min(figsize)*1.7, loc='center left', bbox_to_anchor=(0.4, 0.75))
        plt.xlabel("step")
        plt.ylabel(target_type)
        plt.title(f"The {target_type} value of each step of MCMC (burn in {burn_in})")
        if (Saving_address):
            plt.savefig(Saving_address)
        plt.show()


from matplotlib.patches import Rectangle
from matplotlib.colors import ListedColormap

def density_plots(Thetas, plot_axis, bins, burn_in, axis_name=[], cr_1D=0, cr_2D=0, figsize=(10, 9), cmap='viridis', information="", Saving_address=""):
    """
    Plot the density of each axis and the heat map of each pair of axis    

    Arguments
    ---------
    Thetas (np.array): the value of parameters generated by the MCMC model
    plot_axis (List[int]): the axis plotted by the function
    bins (int): the number of bins of each histogram and heat map
    burn_in (int): the number of the data points want to "burn_in" for the graph
    cr_1D (float): the credible region of each 1D density histogram
    figsize: the figure size of the plots
    cmap: the color map used for the 2D histogram
    information (str): information to be displayed on the right corner of the plot

    Returns
    -------
    None
    """

    if not(plot_axis):
        plot_axis = [i for i in range(Thetas.shape[1])]
    n_axis = len(plot_axis)
    datasize = Thetas.shape[0]
    CR_1D = {}

    with plt.style.context("ggplot"):

        fig, axes = plt.subplots(ncols=n_axis, nrows=n_axis, figsize=figsize)
        for i in range(0,n_axis):
            for j in range(0, i+1):
                if i==j:
                    cs, bs, patches = axes[i, j].hist(Thetas[burn_in:, plot_axis[i]], bins=bins, color="steelblue")
                    if axis_name:
                        axes[i, j].set_xlabel(axis_name[i])
                    else:
                        axes[i, j].set_xlabel(f"$x_{plot_axis[i]}$")
                    axes[i, j].set_ylabel("Counts")
                    if (cr_1D):
                        CR_1D[i] = []
                        posterior_prob = 0
                        posts = cs/(datasize-burn_in)

                        while(posterior_prob<cr_1D):
                            max_pos_idx = np.argmax(posts)
                            posterior_prob += posts[max_pos_idx]
                            posts[max_pos_idx] = -1
                            CR_1D[i].append(bs[max_pos_idx:max_pos_idx+2])
                            patches[max_pos_idx].set_facecolor("#ec2d01")

                else:
                    # Create the heatmap using hist2d
                    counts, x_edges, y_edges = np.histogram2d(Thetas[burn_in:, plot_axis[j]], Thetas[burn_in:, plot_axis[i]], bins=bins)
                    if (cr_2D):
                        # threshold = np.percentile(counts, (1-cr_2D) * 100)
                        r = len(counts)
                        cr_counts = np.sort(counts.flatten())
                        threshold_counts = np.sum(counts)*cr_2D
                        Count = 0
                        while(Count<threshold_counts):
                            r -= 1
                            Count += cr_counts[r]
                        threshold = cr_counts[r]
                        # Create a custom colormap with orange for the credible region and use it for the heatmap
                        cmap_custom = plt.get_cmap(cmap)
                        cmap_custom = ListedColormap(cmap_custom.colors)
                        cmap_custom.set_over("#ec2d01")
                        heatmap = axes[i, j].imshow(counts.T, extent=[x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]], cmap=cmap_custom, origin='lower', aspect='auto', vmax=threshold)
                    else:
                        # Plot the heatmap without the credible region
                        heatmap = axes[i, j].imshow(counts.T, extent=[x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]], cmap=cmap, origin='lower', aspect='auto')

                    if axis_name:
                        axes[i, j].set_xlabel(axis_name[j])
                        axes[i, j].set_ylabel(axis_name[i])
                    else:
                        axes[i, j].set_xlabel(f"$x_{plot_axis[j]}$")
                        axes[i, j].set_ylabel(f"$x_{plot_axis[i]}$")
                    fig.delaxes(axes[j, i])

        # Add colorbar to the whole plot
        cbar_ax = fig.add_axes([0.95, (1/n_axis)*1.08, 0.02, 1-(1/n_axis)*1.18]) # left, bottom, width, height
        fig.colorbar(heatmap, cax=cbar_ax)

        N = "NULL"
        fig.subplots_adjust(right=0.85, wspace=0.3, hspace=0.3)
        legend_text = f"Credible Region(1D) = {cr_1D if cr_1D else N}, Credible Region(2D) = {cr_2D if cr_2D else N}"
        fig.legend(fontsize=14, handles=[Rectangle((0,0),1,1,color="#ec2d01")], labels=[legend_text], loc="upper right", bbox_to_anchor=(1.0, 1.0))  # Adjust the position of the legend to the right upper corner

        # Add the information board on the right-hand corner of the plot, aligned with the legend
        info_ax = fig.add_axes([(1-1/n_axis) * 1.15, 0.87, 0.15, 0.1], frame_on=False)  # left, bottom, width, height
        info_ax.set_xticks([])
        info_ax.set_yticks([])
        info_ax.text(0, 0.5, information, fontsize=12, va='center', bbox=dict(facecolor='white', alpha=0.5, edgecolor='black'))

        fig.tight_layout()

    if (Saving_address):
        plt.savefig(Saving_address)
    plt.show()
    return CR_1D





import plotly.graph_objects as go

def density_plot(Thetas, bins, x_axis=0, y_axis=1, x_name="x", y_name="y", burn_in=0, credible_region=0, figsize=(800, 800), alpha=1, label="", Plot3D=False, Interact3D=False, zoom_in=[], Saving_address=""):
    """
    Plot an interactive 3D heatmap of a pair of dimensions from the input data.

    Arguments:
    Thetas (np.array): the value of parameters generated by the MCMC model
    bins (int): the number of bins of each histogram and heat map
    x_axis (int): the index of the x-axis to plot
    y_axis (int): the index of the y-axis to plot
    x_name (string): the name of the x-axis to plot
    y_name (string): the name of the y-axis to plot
    burn_in (int): the number of the data points want to "burn_in" for the graph
    credible_region (float): the size of the credible region in percent
    figsize (tuple): the size of the figure
    label (string): the label want to add to the plot
    Save_fig (bool): decide whether to save the output figure of the function
    fig_name (string): the saved figure name
    zoom_in (List): the part of the graph want to zoom in

    Returns:
    None
    """
    Thetas = np.asarray(Thetas)
    if (zoom_in):
        Thetas = Thetas[np.logical_and(np.logical_and(Thetas[:,0]>=zoom_in[0][0], Thetas[:,0]<=zoom_in[0][1]), np.logical_and(Thetas[:,1]>=zoom_in[1][0], Thetas[:,1]<=zoom_in[1][1]))]

    # prepare the data for the 2D histogram
    hist, xedges, yedges = np.histogram2d(Thetas[burn_in:, x_axis], Thetas[burn_in:, y_axis], bins=bins)
    hist = hist.T
    xmid = 0.5*(xedges[1:] + xedges[:-1])
    ymid = 0.5*(yedges[1:] + yedges[:-1])
    X, Y = np.meshgrid(xmid, ymid)

    if Plot3D:
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='3d')

        if (credible_region):
            datasize = Thetas.shape[0]
            credible_value = credible_region*datasize-burn_in
            # create mask for credible region
            cr_mask = np.zeros_like(hist)
            posts_prob = 0
            posts = hist.copy()
            max_pos_idx = np.argmax(posts)
            max_x = int(max_pos_idx//bins)
            max_y = int(max_pos_idx%bins)
            posts_prob += posts[max_x, max_y]
            posts[max_x, max_y] = -1
            cr_mask[max_x, max_y] = 1
            max_hist = hist[max_x, max_y]
            # marking the bins inside the credible region
            while(posts_prob<credible_value):
                max_pos_idx = np.argmax(posts)
                max_x = int(max_pos_idx//bins)
                max_y = int(max_pos_idx%bins)
                posts_prob += posts[max_x, max_y]
                posts[max_x, max_y] = -1
                cr_mask[max_x, max_y] = 1
            del posts
            # plot the density plot of the inputted data
            ax.plot_surface(X, Y, hist, facecolors=plt.cm.viridis(cr_mask.T), alpha=alpha)
            fig.colorbar(ax.plot_surface(X, Y, hist, facecolors=plt.cm.viridis(cr_mask.T)))
            # create 3D heatmap with the data prepared above
            ax.set_title(f"3D density plot of {x_name} and {y_name} with credible region {credible_region}"+label)
        else:
            # plot the density
            # plot the density plot of the inputted data
            ax.plot_surface(X, Y, hist, cmap='viridis', alpha=alpha)
            # # Add contour plots
            # cset = ax.contour(X, Y, hist.T, zdir='z', offset=np.min(hist), cmap=plt.cm.coolwarm)
            # cset = ax.contour(X, Y, hist.T, zdir='x', offset=np.min(xedges), cmap=plt.cm.coolwarm)
            # cset = ax.contour(X, Y, hist.T, zdir='y', offset=np.max(yedges), cmap=plt.cm.coolwarm)

            fig.colorbar(ax.plot_surface(X, Y, hist, cmap='viridis'))
            # create 3D heatmap with the data prepared above
            ax.set_title(f"3D density plot of {x_name} and {y_name}"+label)

        max_idx = np.argmax(hist)
        X_max = X[max_idx//hist.shape[0], max_idx%hist.shape[0]]
        Y_max = Y[max_idx//hist.shape[0], max_idx%hist.shape[0]]
        hist_max = hist[max_idx//hist.shape[0], max_idx%hist.shape[0]]
        ax.scatter(X_max, Y_max, hist_max, c="red", marker='o', linewidths=2, label=f"The Maximum density point ({x_name}, {y_name}) = ({X_max:.3f} , {Y_max:.3f})")
        ax.set_xlabel(x_name)
        ax.set_ylabel(y_name)
        ax.set_zlabel("Counts")
        ax.legend()
        ax.set_box_aspect([1, 1, 0.7])
        # ax.view_init(elev=-1.7, azim=-1.7)
        ax.dist = 10

        plt.tight_layout()

        if (Saving_address):
            plt.savefig(Saving_address)

        plt.show()
    elif Interact3D:
        if (credible_region):
            datasize = Thetas.shape[0]
            credible_value = credible_region*datasize-burn_in
            # create mask for credible region
            cr_mask = np.zeros_like(hist)
            posts_prob = 0
            posts = hist.copy()
            max_pos_idx = np.argmax(posts)
            max_x = int(max_pos_idx//bins)
            max_y = int(max_pos_idx%bins)
            posts_prob += posts[max_x, max_y]
            posts[max_x, max_y] = -1
            cr_mask[max_x, max_y] = 1
            max_hist = hist[max_x, max_y]
            # marking the bins inside the credible region
            while(posts_prob<credible_value):
                max_pos_idx = np.argmax(posts)
                max_x = int(max_pos_idx//bins)
                max_y = int(max_pos_idx%bins)
                posts_prob += posts[max_x, max_y]
                posts[max_x, max_y] = -1
                cr_mask[max_x, max_y] = 1
            del posts
            # ploting the density plot of the inputed data
            fig = go.Figure(data=[go.Surface(x=X, y=Y, z=hist, surfacecolor=cr_mask, colorscale="Viridis", opacity=alpha)])
            # create 3D heatmap with the data prepared above
            fig.update_layout(
                title=f"3D density plot of {x_name} and {y_name} with credible region {credible_region}"+label,
                autosize=False,
                width=figsize[0],
                height=figsize[1],
                scene=dict(
                    xaxis_title=x_name,
                    yaxis_title=y_name,
                    zaxis_title="counts",
                    aspectratio=dict(x=1, y=1, z=0.7),
                    camera_eye=dict(x=-1.7, y=-1.7, z=0.5),
                    dragmode="orbit",
                    ),
            )
        else:
            # ploting the density plot of the inputed data
            fig = go.Figure(data=[go.Surface(x=X, y=Y, z=hist , colorscale="viridis", opacity=alpha)])
            # create 3D heatmap with the data prepared above
            fig.update_layout(
                title=f"3D density plot of {x_name} and {y_name}"+label,
                autosize=False,
                width=figsize[0],
                height=figsize[1],
                scene=dict(
                    xaxis_title=x_name,
                    yaxis_title=y_name,
                    zaxis_title="counts",
                    aspectratio=dict(x=1, y=1, z=0.7),
                    camera_eye=dict(x=-1.7, y=-1.7, z=0.5),
                    dragmode="orbit",
                    ),
            )
        fig.show()
    else:
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111)

        # plot the density plot of the inputted data
        ax.imshow(hist, cmap='viridis', origin='lower', alpha=alpha, extent=[X.min(), X.max(), Y.min(), Y.max()], aspect='auto')
        fig.colorbar(ax.imshow(hist, cmap='viridis', origin='lower', alpha=alpha, extent=[X.min(), X.max(), Y.min(), Y.max()], aspect='auto'))

        # create 3D heatmap with the data prepared above
        ax.set_title(f"2D density plot of {x_name} and {y_name}"+label)

        max_idx = np.argmax(hist)
        X_max = X[max_idx//hist.shape[0], max_idx%hist.shape[0]]
        Y_max = Y[max_idx//hist.shape[0], max_idx%hist.shape[0]]
        ax.scatter(X_max, Y_max, c="red", marker='o', linewidths=2, label=f"The Maximum density point ({x_name}, {y_name}) = ({X_max:.3f}, {Y_max:.3f})")
        ax.set_xlabel(x_name)
        ax.set_ylabel(y_name)
        ax.legend()
        # ax.view_init(elev=-1.7, azim=-1.7)
        ax.dist = 10

        plt.tight_layout()

        if (Saving_address):
            plt.savefig(Saving_address)

        plt.show()




def Target_Distribution_Visualization(X_range: List, Y_range: List, Tar_Dis: object, Func_name: str, alpha=1, Plot3D=False, Interact3D=False, Saving_address=""):

    """

    Plotting the 3D plot of the Target Distribution of the MCMC algorithm

    Arguments
    ---------
    X_range (List[float]): the range of the x axis of the plot
    Y_range (List[float]): the range of the y axis of the plot
    Tar_Dis (Callable): the target distritbution to visualize
    Func_name (string): the name of the function to be visualized
    alpha (float): the alpha transparency of the plot
    Single_vision (bool): deciding whether to plot interactable plot

    Returns
    -------
    None
    
    """

    # Define thei grid 
    X_val = np.linspace(X_range[0], X_range[1], 100)
    Y_val = np.linspace(Y_range[0], Y_range[1], 100)
    X_grid, Y_grid = np.meshgrid(X_val, Y_val)

    # Compute the values of the z-axis
    Z_grid = Tar_Dis(np.column_stack((X_grid.flatten(), Y_grid.flatten())))
    Z_grid = Z_grid.reshape(X_grid.shape)

    if Plot3D:
        # Creat the surface plot
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(X_grid, Y_grid, Z_grid, cmap='viridis', alpha=alpha)
        fig.colorbar(ax.plot_surface(X_grid, Y_grid, Z_grid, cmap='viridis'))

        # Set the plot title and axis labels
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("f(X, Y)")
        ax.set_title(Func_name)
        plt.tight_layout()

        if (Saving_address):
            plt.savefig(Saving_address)

        plt.show()
    
    elif Interact3D:
        # Create the surface plot
        fig = go.Figure(data = [go.Surface(x=X_grid, y=Y_grid, z=Z_grid, colorscale="Viridis", opacity=alpha)])

        # Set the plot title and axis labels
        fig.update_layout(
            width=800,
            height=800,
            title = Func_name,
            scene = dict(
                xaxis_title = "X",
                yaxis_title = "Y",
                zaxis_title = "f(X, Y)",
            )
        )

        if (Saving_address):
            plt.savefig(Saving_address)

        fig.show()
    
    else:
        # Creat the 2D heatmap plot
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111)
        ax.imshow(Z_grid, cmap='viridis', origin='lower', alpha=alpha, extent=[X_grid.min(), X_grid.max(), Y_grid.min(), Y_grid.max()], aspect="auto")
        fig.colorbar(ax.imshow(Z_grid, cmap='viridis', origin='lower', alpha=alpha, extent=[X_grid.min(), X_grid.max(), Y_grid.min(), Y_grid.max()], aspect="auto"))

        # Set the plot title and axis labels
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title(Func_name)
        plt.tight_layout()

        if (Saving_address):
            plt.savefig(Saving_address)

        plt.show()

def PlotHeatmap(x, y, z, xlabel, ylabel, zlabel, Plot_Max=False, Plot3D=False, Saving_address=""):
    if Plot3D:
        # Creat the surface plot
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(x, y, z, cmap='viridis', alpha=1)
        fig.colorbar(ax.plot_surface(x, y, z, cmap='viridis'))
        max_idx = np.argmax(z)
        if Plot_Max:
            row = int(max_idx/z.shape[1])
            col = int(max_idx%z.shape[1])
            x_max = x[row, col]
            y_max = y[row, col]
            z_max = z[row, col]
            ax.scatter(x_max, y_max, z_max, c='red', marker='o', linewidths=2, label=f"The Maxumum likelihood point ({xlabel}, {ylabel}) = ({x_max:.3f}, {y_max:.3f})")
            ax.legend()

        # Set the plot title and axis labels
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_zlabel(zlabel)
    else:
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111)
        ax.imshow(z, cmap='viridis', origin='lower', extent=[x.min(), x.max(), y.min(), y.max()], aspect='auto')
        fig.colorbar(ax.imshow(z, cmap='viridis', origin='lower', extent=[x.min(), x.max(), y.min(), y.max()], aspect='auto'))
        max_idx = np.argmax(z)
        if Plot_Max:
            x_max = x[max_idx//z.shape[1], max_idx%z.shape[1]]
            y_max = y[max_idx//z.shape[1], max_idx%z.shape[1]]
            ax.scatter(x_max, y_max, c='red', marker='o', linewidths=2, label=f"The Maxumum likelihood point ({xlabel}, {ylabel}) = ({x_max:.3f}, {y_max:.3f})")
            ax.legend()

        # Set the plot title and axis labels
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

    plt.tight_layout()

    if (Saving_address):
        plt.savefig(Saving_address)
            
    plt.show()

import plotly

def UpdatingPlot(Data, Data_range, high_light_points=10):
    """
    Plot the updating points of the MCMC algorithm

    
    """
    # Circle properties
    circle_width = 1
    circle_color = 'green'

    # Create initial scatter plot
    scatter = go.Scatter(
        x=[Data[Data_range[0], 0]],
        y=[Data[Data_range[0], 1]],
        mode='markers',
        marker=dict(color='red')
    )

    # Create empty circle trace
    circle = go.Scatter(
        x=[],
        y=[],
        mode='markers',
        marker=dict(
            size=circle_width,
            color=circle_color,
            line=dict(width=1, color=circle_color)
        )
    )

    # Create figure
    fig = go.Figure(data=[scatter, circle])

    # Set layout
    fig.update_layout(
        xaxis=dict(range=[Data[:, 0].min(), Data[:, 0].max()]),
        yaxis=dict(range=[Data[:, 1].min(), Data[:, 1].max()]),
        width=600,
        height=600
    )

    # Animation frames
    frames = []
    for i in range(Data_range[1] - Data_range[0]):
        x = Data[:i+1, 0]
        y = Data[:i+1, 1]

        # Determine colors for the points
        colors = ['red'] * max([i-high_light_points, 0]) + ['green']*9 + ['blue'] 
        # Create scatter trace with updated colors
        scatter = go.Scatter(x=x, y=y, mode='markers', marker=dict(color=colors))

        frame = go.Frame(data=[scatter, circle], layout=go.Layout(transition={'duration': 100, 'easing': 'linear'}))
        frames.append(frame)

    # Add frames to the figure
    fig.frames = frames

    # Play animation in an infinite loop
    fig.update_layout(
        updatemenus=[dict(
            type='buttons',
            buttons=[dict(
                label='Play',
                method='animate',
                args=[None, {
                    'frame': {'duration': 100, 'redraw': True},
                    'fromcurrent': True,
                    'mode': 'immediate',
                    'transition': {'duration': 0}
                }],
            )],
        )]
    )

    # Show the animation
    plotly.offline.plot(fig)