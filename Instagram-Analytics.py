import instaloader
import pandas as pd
import matplotlib.pyplot as plt
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

        # Iterate through posts
        for post in profile.get_posts():
            post_date = post.date
            if start_date <= post_date <= end_date:
                posts_data.append({
                    "Date": post_date,
                    "Likes": post.likes,
                    "Comments": post.comments,
                    "Caption": post.caption[:50] if post.caption else "No caption",  # Truncate for brevity
                    "URL": f"https://www.instagram.com/p/{post.shortcode}/"
                })
            # Stop if we've gone past the start date (posts are in reverse chronological order)
            if post_date < start_date:
                break

        return posts_data

    except Exception as e:
        print(f"Error fetching posts: {e}")
        return []

# Function to calculate engagement metrics
def calculate_engagement(posts_data, username):
    df = pd.DataFrame(posts_data)
    if df.empty:
        print("No posts found in the specified date range.")
        return None

    # Calculate total engagement (Likes + Comments)
    df["Engagement"] = df["Likes"] + df["Comments"]
    
    # Fetch follower count for engagement rate calculation
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        followers = profile.followers
        df["Engagement_Rate"] = (df["Engagement"] / followers) * 100  # Percentage
    except:
        df["Engagement_Rate"] = None  # Set to None if unable to fetch followers

    return df

# Function to export data to Excel
def export_to_excel(df, username, start_date, end_date):
    if df is not None and not df.empty:
        filename = f"{username}_engagement_{start_date}_to_{end_date}.xlsx"
        with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Engagement Data")

        print(f"📊 Data successfully saved to **{filename}**")

# Function to plot engagement charts
def plot_engagement_charts(df, username, start_date, end_date):
    if df is None or df.empty:
        print("No data to plot.")
        return

    # Convert Date to string for plotting
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    # Plot 1: Engagement over time
    plt.figure(figsize=(10, 6))
    plt.plot(df["Date"], df["Engagement"], marker="o", label="Engagement (Likes + Comments)")
    plt.title(f"Engagement Over Time (@{username}) {start_date} to {end_date}")
    plt.xlabel("Date")
    plt.ylabel("Engagement")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Plot 2: Engagement Rate over time
    plt.figure(figsize=(10, 6))
    plt.plot(df["Date"], df["Engagement_Rate"], marker="o", color="green", label="Engagement Rate (%)")
    plt.title(f"Engagement Rate Over Time (@{username}) {start_date} to {end_date}")
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
    # User input for Instagram username and date range
    username = input("Enter Instagram Username: ")
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
    df = calculate_engagement(posts_data, username)
    if df is not None:
        print("\n📈 Engagement Analytics Report:")
        print(df[["Date", "Likes", "Comments", "Engagement", "Engagement_Rate"]])

        # Export to Excel
        export_to_excel(df, username, start_date, end_date)

        # Plot charts
        plot_engagement_charts(df, username, start_date, end_date)

if __name__ == "__main__":
    main()
