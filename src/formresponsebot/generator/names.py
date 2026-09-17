import random


class SyntheticNameGenerator:
    """
    Generates unique synthetic Indian-style names.

    The names are intended for synthetic/test data only.
    """

    FIRST_NAMES = [
        "Aarav",
        "Aditya",
        "Akash",
        "Aman",
        "Amit",
        "Aniket",
        "Anirudh",
        "Ankit",
        "Arjun",
        "Ashish",
        "Ayush",
        "Deepak",
        "Dhruv",
        "Gaurav",
        "Harsh",
        "Karan",
        "Kartik",
        "Manish",
        "Mohit",
        "Nikhil",
        "Rahul",
        "Rajat",
        "Rakesh",
        "Rohan",
        "Rohit",
        "Sagar",
        "Saurav",
        "Shubham",
        "Siddharth",
        "Vikas",
        "Vivek",
        "Abhishek",
        "Ananya",
        "Anushka",
        "Aditi",
        "Bhavana",
        "Divya",
        "Isha",
        "Kavya",
        "Megha",
        "Neha",
        "Nikita",
        "Pallavi",
        "Pooja",
        "Priya",
        "Riya",
        "Sakshi",
        "Shreya",
        "Simran",
        "Sneha",
        "Sonali",
        "Swati"
    ]

    SURNAMES = [
        "Mohanty",
        "Patnaik",
        "Das",
        "Behera",
        "Nayak",
        "Sahu",
        "Jena",
        "Pradhan",
        "Mishra",
        "Rout",
        "Panda",
        "Barik",
        "Samal",
        "Sethy",
        "Tripathy",
        "Acharya",
        "Biswal",
        "Mahapatra",
        "Swain",
        "Dhal",
        "Parida",
        "Maharana",
        "Lenka",
        "Rath",
        "Kar",
        "Bhoi",
        "Dash",
        "Gouda",
        "Behera",
        "Mishra"
    ]

    def __init__(self):
        self.used_names = set()

    def generate(self):
        """
        Generate a unique synthetic name.
        """

        # Try several combinations before falling back
        # to a numbered variation.
        for _ in range(100):

            first_name = random.choice(self.FIRST_NAMES)
            surname = random.choice(self.SURNAMES)

            full_name = f"{first_name} {surname}"

            if full_name not in self.used_names:
                self.used_names.add(full_name)
                return full_name

        # Extremely unlikely fallback when combinations are exhausted.
        number = len(self.used_names) + 1
        full_name = f"Synthetic Respondent {number}"

        self.used_names.add(full_name)

        return full_name

    def reset(self):
        """Clear the list of previously generated names."""

        self.used_names.clear()