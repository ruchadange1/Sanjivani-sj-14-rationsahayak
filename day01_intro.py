project_name = "RationSahayak"
product = "AI-powered ration assistance system for Maharashtra citizens"
user = "Migrant construction worker from Beed living in Kopargaon with a family of five"
problem = "Does not know ration card benefits, monthly grain entitlement and ONORC portability"
data_source = "DFPD FAQ, NFSA Portal and Maharashtra MahaFood"

# Display project card using f-strings

print("\n========== RATIONSAHAYAK PROJECT CARD ==========")

print(f"Project Name : {project_name}")
print(f"Product      : {product}")
print(f"User         : {user}")
print(f"Problem      : {problem}")
print(f"Data Source  : {data_source}")

print("================================================")

# Get user input

name = input("\nEnter your name: ")
question = input("Enter your ration-related question: ")

print(f"\nHello, {name}!")
print(f"Your question is: {question}")
