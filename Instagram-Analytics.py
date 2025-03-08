import instaloader
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import time
import random
import math

# Initialize Instaloader
L = instaloader.Instaloader()

# Function to fetch posts from an Instagram profile within a date range
def fetch_instagram_posts(username, start_date, end_date, max_posts=10):
    try:
        # Load profile
        profile = instaloader.Profile.from_username(L.context, username)
        posts_data = []

        # Convert date strings to datetime objects
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Get total number of posts for progress bar
        total_posts = sum(1 for post in profile.get_posts())  # Count total posts for percentage tracking
        print(f"Total posts to fetch: {total_posts}")

        # Get followers at the start date
        start_followers = profile.followers

        # Iterate through posts
        fetched_posts = 0
        retries = 0
        max_retries = 5  # Max retries before failing
        retry_delay_base = 30  # Base time to wait before retry (in seconds)

        for post in profile.get_posts():
            try:
                post_date = post.date
                if start_date <= post_date <= end_date:
                    posts_data.append({
                        "Date": post_date,
                        "Likes": post.likes,
                        "Comments": post.comments,
                        "Caption": post.caption[:50] if post.caption else "No caption",  # Truncate for brevity
                        "URL": post.shortcode
                    })

                # Update progress bar
                fetched_posts += 1
                percentage = (fetched_posts / total_posts) * 100
                print(f"Loading... {math.ceil(percentage)}% complete", end='\r')

                # Stop fetching after reaching the max_posts limit
                if fetched_posts >= max_posts:
                    break

                # Add a random delay between 10 minutes to 1 hour to mimic organic browsing
                delay_time = random.uniform(600, 3600)  # Random delay between 10 minutes and 1 hour
                print(f"\nSleeping for {delay_time:.2f} seconds...")
                time.sleep(delay_time)

            except Exception as e:
                # Handle rate limits and temporary blocks
                print(f"\nError fetching post: {e}")
                if retries < max_retries:
                    retries += 1
                    retry_delay = retry_delay_base * (2 ** retries) + random.randint(5, 15)  # Exponential backoff
                    print(f"Retrying in {retry_delay} seconds... (Retry #{retries})")
                    time.sleep(retry_delay)
                    continue
                else:
                    print("Max retries reached. Exiting.")
                    break

        print("\nFetch completed.")

        # Get followers at the end date
        end_followers = profile.followers

        # Calculate follower growth
        follower_growth = end_followers - start_followers
        print(f"Follower Growth: {follower_growth} followers (Start: {start_followers}, End: {end_followers})")

        return posts_data, start_followers, end_followers, follower_growth

    except Exception as e:
        print(f"Error fetching posts: {e}")
        return [], None, None, None

# Function to calculate engagement metrics
def calculate_engagement(posts_data):
    df = pd.DataFrame(posts_data)
    if df.empty:
        print("No posts found in the specified date range.")
        return None

    # Calculate total engagement (Likes + Comments)
    df["Engagement"] = df["Likes"] + df["Comments"]
    
    # Engagement rate (assuming followers count is needed; here we'll estimate or fetch if possible)
    profile = instaloader.Profile.from_username(L.context, "wubwagon")  # Modify username if needed
    followers = profile.followers
    df["Engagement_Rate"] = df["Engagement"] / followers * 100  # Percentage

    return df

# Function to plot engagement charts
def plot_engagement_charts(df, start_date, end_date):
    if df is None or df.empty:
        print("No data to plot.")
        return

    # Convert Date to string for plotting
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    # Plot 1: Engagement over time
    plt.figure(figsize=(10, 6))
    plt.plot(df["Date"], df["Engagement"], marker="o", label="Engagement (Likes + Comments)")
    plt.title(f"Engagement Over Time (@wubwagon) {start_date} to {end_date}")
    plt.xlabel("Date")
    plt.ylabel("Engagement")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Plot 2: Engagement Rate over time
    plt.figure(figsize=(10, 6))
    plt.plot(df["Date"], df["Engagement_Rate"], marker="o", color="green", label="Engagement Rate (%)")
    plt.title(f"Engagement Rate Over Time (@wubwagon) {start_date} to {end_date}")
    plt.xlabel("Date")
    plt.ylabel("Engagement Rate (%)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Plot 3: Bar chart of Likes vs Comments
    df.plot(kind="bar", x="Date", y=["Likes", "Comments"], figsize=(12, 6), title="Likes vs Comments")
    plt.xlabel("Date")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Function to export the data to an Excel file
def export_to_excel(df, start_date, end_date):
    filename = f"instagram_analytics_{start_date}_to_{end_date}.xlsx"
    df.to_excel(filename, index=False, engine='xlsxwriter')
    print(f"Data exported to {filename}")

# Main function to run the analysis
def main():
    # User input for Instagram username and date range
    print("Enter Instagram Username (without @): ")
    username = input().strip()
    
    print("Enter the date range for analysis (format: YYYY-MM-DD)")
    start_date = input("Start Date: ")
    end_date = input("End Date: ")

    # Validate date format
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return

    # Fetch posts and follower data
    print(f"Fetching posts for @{username} from {start_date} to {end_date}...")
    posts_data, start_followers, end_followers, follower_growth = fetch_instagram_posts(username, start_date, end_date, max_posts=10)

    # Calculate engagement
    df = calculate_engagement(posts_data)
    if df is not None:
        print("\nEngagement Analytics:")
        print(df[["Date", "Likes", "Comments", "Engagement", "Engagement_Rate"]])

        # Plot charts
        plot_engagement_charts(df, start_date, end_date)

        # Export to Excel
        export_to_excel(df, start_date, end_date)

        # Display follower growth
        print(f"\nFollower Growth: {follower_growth} followers (Start: {start_followers}, End: {end_followers})")

if __name__ == "__main__":
    main()
