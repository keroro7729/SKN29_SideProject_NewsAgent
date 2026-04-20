from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List

class NewsSummary(BaseModel):
    category: str = Field(description="기사 내용의 카테고리")
    summary: str = Field(description="기사 내용 요약")
    tags: List[str] = Field(description="기사 내용의 핵심 키워드 3~5개")

class NewsRefineService:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-4.1-mini")
        self.structured_llm = self.llm.with_structured_output(NewsSummary)
        self.prompt = PromptTemplate.from_template(
            "다음에 오는 기사 내용을 분석해 주세요\n\n {news_content}"
            "카테고리는 사회, 경제, 연예, 스포츠 중에서만 답변하고 이 외의 답변은 하지 말 것"
            "기사 내용 요약은 5문장 이내로 할 것"
        )
        self.chain = self.prompt | self.structured_llm
        
    # 답변 결과 생성
    def get_summary_category(self, news_content) -> NewsSummary:
        result = self.chain.invoke(
            {
                "news_content": news_content,
            }
        )
        
        return result