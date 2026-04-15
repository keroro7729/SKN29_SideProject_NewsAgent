from langchain.agents import create_agent

class ChatBotService:
    def __init__(self):
        # 챗봇 에이전트 생성
        self.agent = create_agent(
            model="openai:gpt-4.1-mini",
            tools=[],
            system_prompt=(
                "너는 사용자의 쿼리에 응답하는 에이전트다"
                "사용자의 질문에 거짓없이 진실하게 답하라"
                "모르는 질문에 대해서는 아는 척 하지 말고 모른다고 답하라"
            ),
        )
        
    # 답변 결과 생성
    def response(self, content):
        result = self.agent.invoke({
            "messages": [{"role": "user", "content": content }]
        })
        
        return result['messages'][1].content