import instaloader
import random
import time
import pandas as pd
from datetime import datetime

# Initialize Instaloader
L = instaloader.Instaloader()

# Function to fetch posts from an Instagram profile within a date range
def fetch_instagram_posts(username, start_date, end_date):
    try:
        # Load profile
        profile = instaloader.Profile.from_username(L.context, username)
        posts_data = []

        # Convert date strings to datetime objects
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Introduce some randomization in the requests
        retry_attempts = 10  # Increase the retry attempts for robustness
        backoff_time = 30  # Initial backoff time in seconds

        for attempt in range(retry_attempts):
            try:
                # Iterate through posts
                for post in profile.get_posts():
                    post_date = post.date
                    if start_date <= post_date <= end_date:
                        posts_data.append({
                            "Date": post_date,
                            "Likes": post.likes,
                            "Comments": post.comments,
                            "Caption": post.caption[:50] if post.caption else "No caption",  # Truncate for brevity
                            "URL": post.shortcode
                        })
                    
                    # Stop if we've gone past the start date (posts are in reverse chronological order)
                    if post_date < start_date:
                        break

                # If posts are fetched successfully, break out of retry loop
                if posts_data:
                    break

            except Exception as e:
                print(f"Error in attempt {attempt + 1}: {e}")
                if attempt < retry_attempts - 1:
                    # Exponential backoff with randomization
                    wait_time = random.randint(backoff_time, backoff_time + 90)  # 30 to 90 seconds
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    # Double the backoff time after each failure to make the retries slower
                    backoff_time = random.randint(60, 180)  # randomize further
                else:
                    print("Max retries reached. Exiting.")
                    return []

        return posts_data

    except Exception as e:
        print(f"Error fetching posts: {e}")
        return []

# Function to calculate engagement metrics
def calculate_engagement(posts_data):
    df = pd.DataFrame(posts_data)
    if df.empty:
        print("No posts found in the specified date range.")
        return None

    # Calculate total engagement (Likes + Comments)
    df["Engagement"] = df["Likes"] + df["Comments"]
    
    # Estimate followers count (this is where you may need to add a real follower count fetch)
    profile = instaloader.Profile.from_username(L.context, "wubwagon")
    followers = profile.followers  # Assuming you have access to the followers count
    df["Engagement_Rate"] = df["Engagement"] / followers * 100  # Engagement rate as a percentage

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

# Main function to run the analysis
def main():
    # User input for username and date range
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

    # Fetch posts
    print(f"Fetching posts for @{username} from {start_date} to {end_date}...")
    posts_data = fetch_instagram_posts(username, start_date, end_date)

    # Calculate engagement
    df = calculate_engagement(posts_data)
    if df is not None:
        print("\nEngagement Analytics:")
        print(df[["Date", "Likes", "Comments", "Engagement", "Engagement_Rate"]])

        # Plot charts
        plot_engagement_charts(df, start_date, end_date)

if __name__ == "__main__":
    main()
