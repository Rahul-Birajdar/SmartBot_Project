import openai

openai.api_key="AIzaSyBRMh11gAThUvN0j4iZ7SRVY9wP-0Xe8vc"
def chat_with_gpt(prompt):
# Use the correct method call for the ChatCompletion
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
if __name__=="__main__":
    while True:
        user_input=input("You: ")
        if user_input.lower() in ["quit","exit","bye"]:
            break
        response=chat_with_gpt(user_input)
        print("Chatbot: ",response)