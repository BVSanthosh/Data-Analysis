#!/usr/bin/env python
from datetime import datetime
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import os
from ipywidgets import fixed, interactive

# Stores the filepath to the images directory
IMAGE_DIRECTORY = "../images/"

"""
This file contains a number of helper methods that take an analysed data set and uses it to create figures.

This allows for them to be loaded in and used in a jupyter notebook which has a data set from analyseData loaded in too.

It also contains a method to create and save all visuals in the images directory.
"""


# Plots a bar chart with the counts for the Top N users replied to.
def plot_top_user_replies(data, n):
    reply_data = data.top_n_user_interactions(n)

    # Setting up the figure and its axes
    fig = plt.figure(figsize=(20, 8))

    axes = fig.add_axes([0, 0, 1, 1])

    fig.suptitle(f'Top {n} users replied to')
    usernames = [record[0] for record in reply_data]
    reply_counts = [record[1] for record in reply_data]

    # Plotting the bar chart and returning its figure
    axes.bar(usernames, reply_counts)

    return fig

# Plots a bar chart with the counts for the Top N users retweeted to.
def plot_top_user_retweeted(data, n):
    rt_data = data.top_n_user_rt(n)

    # Setting up the figure and its axes
    fig = plt.figure(figsize=(20, 8))

    axes = fig.add_axes([0, 0, 1, 1])

    fig.suptitle(f'Top {n} users retweeted to')
    usernames = [record[0] for record in rt_data]
    rt_counts = [record[1] for record in rt_data]

    # Plotting the bar chart and returning its figure
    axes.bar(usernames, rt_counts)

    return fig

# Plots a word cloud of the hashtags outside of the Top N
def hashtags_wordcloud(data, n=10):
    # Finds the data for the Top N Hashtags from the AnalysedDataSet.
    top_n_hashtags = data.top_n_hashtags(n)

    # Copies the hashtag dictionary from the AnalysedDataSet.
    hashtags_data = data.hashtags_data.copy()

    # Removes the Top N Hashtags from the dictionary
    for hashtag in top_n_hashtags:
        del hashtags_data[hashtag[0]]

    # Generates a word cloud from the updated copy of the dictionary
    wc = WordCloud(height=600, width=1200, background_color="white").generate_from_frequencies(hashtags_data)

    # Setting up the figure and its axes
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])

    # Setting an appropriate subtitle
    fig.suptitle(f'Hashtags after the Top {n}')

    # Plotting the word cloud and returning its figure (Axes are turned off as they are not appropriate for this visual)
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")

    return fig


# Plots a line chart of the tweet activity across time
def activity_timeline(data):
    # Setting up the figure and its axes
    fig = plt.figure(figsize=(20, 8))
    ax = fig.add_axes([0, 0, 1, 1])

    # Setting an appropriate subtitle and harvesting the relevant data from the AnalysedDataSet.
    fig.suptitle('Timeline of Activity')

    # The key values are parsed to datetime to allow for automatic handling of x-axis labels
    dates = [datetime.strptime(date, "%Y-%m-%d %H:%M:%S") for date in data.timeline_data.keys()]
    counts = list(data.timeline_data.values())

    # Reversing the order of the dates and counts so they go in chronological order.
    dates.reverse()
    counts.reverse()

    # Plotting the line chart and returning its figure
    ax.plot(dates, counts)

    return fig


# Plots a bar chart with the counts for the Top N Hashtags.
def plot_top_n_bar_chart(func, text, n=10):
    # Finds the data for the Top N Hashtags from the AnalysedDataSet.
    relevant_data = func(n)
    # Setting up the figure and its axes
    fig = plt.figure(figsize=(20, 8))
    ax = fig.add_axes([0, 0, 1, 1])

    # Setting an appropriate subtitle and harvesting the relevant data from the list of tuples.
    fig.suptitle(f'Top {n}' + " " + text)
    x_values = [record[0] for record in relevant_data]
    y_values = [record[1] for record in relevant_data]

    # Plotting the bar chart and returning its figure
    ax.bar(x_values, y_values)

    return fig

# Plots a pie chart with the share percentage for the Top N Apps.
def app_pie_chart(data, n=10):
    # Setting up the figure
    fig = plt.figure(figsize=(20, 8))

    # Data to plot
    relevant_data = data.top_n_apps(data.app_count)
    labelsTemp = [record[0] for record in relevant_data]
    sizesTemp = [record[1] for record in relevant_data]

    # Summarising shares after the top 10 to tidy graph
    labels = labelsTemp[:n] + ["Others"]
    sizes = sizesTemp[:n] + [sum(sizesTemp[n:])]

    # Plot
    plt.pie(sizes, labels=labels, autopct='%1.2f%%')
    return fig

# Plots a bar chart with the counts for the Top N Hashtags.
def plot_top_hashtags(data, n=10):
    return plot_top_n_bar_chart(data.top_n_hashtags, 'Most Frequent Hashtags', n)


# Plots a bar chart with the counts for the Top N Most Frequent Apps.
def plot_top_apps(data, n=10):
    return plot_top_n_bar_chart(data.top_n_apps, 'Most Frequent Apps', n)


# Plots a bar chart with the counts for the Top N Most Replied to Users.
def plot_top_interactions(data, n=10):
    return plot_top_n_bar_chart(data.top_n_user_interactions, 'Most Frequently Replied to Users', n)


# Plots a bar chart with the counts for the Top N Most Retweeted Users.
def plot_top_rt_users(data, n=10):
    return plot_top_n_bar_chart(data.top_n_user_rt, 'Most Frequently Retweeted Users', n)


# Plots a bar chart with the counts for the Top N Users based on Reply vs Replied to Ratio.
def plot_top_replied_ratios(data, n=10):
    return plot_top_n_bar_chart(data.top_n_users_ratioed_to, 'Users with Highest Reply vs Replied To Ratio', n)


# Plots a bar chart with the counts for the Top N Replied to Hashtags.
def plot_top_replied_hashtags(data, n=10):
    return plot_top_n_bar_chart(data.top_n_hashtags_replied_to, 'Most Frequently Replied to Hashtags', n)


# Takes a figure generator method and creates an interactive visual from it.
def create_interactive_visual(data, generator):
    return interactive(generator, data=fixed(data), n=(1, len(data.hashtags_data) -1))


# Runs the helper method to create each visual, creates the image directory if it doesn't exist and saves each visual
def save_visuals(data, n):
    # Creating the visuals and storing them in a list of figures to be saved
    completed_figures = [plot_top_hashtags(data, n),
                         activity_timeline(data),
                         hashtags_wordcloud(data, n),
                         plot_top_apps(data, n),
                         plot_top_interactions(data, n),
                         plot_top_rt_users(data, n),
                         plot_top_replied_ratios(data, n),
                         plot_top_replied_hashtags(data, n),
                         app_pie_chart(data, n)]


    # Creating the images directory if it doesn't exist
    os.makedirs(os.path.dirname(IMAGE_DIRECTORY), exist_ok=True)

    # Saving the visuals to the directory by iterating through the list of figures
    count = 0
    for visual in completed_figures:
        count += 1
        visual.savefig((IMAGE_DIRECTORY + ("figure_" + str(count) + ".png")), bbox_inches="tight", dpi=300)
