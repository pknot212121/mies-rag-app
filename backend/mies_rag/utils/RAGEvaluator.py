import json
import os
from langchain_groq import ChatGroq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from ragas import evaluate as ragasEvaluate
from ragas.metrics import (
    Faithfulness,
    LLMContextPrecisionWithoutReference,
    ResponseRelevancy,
)
from ragas import SingleTurnSample
from ragas import EvaluationDataset as RagasEvaluationDataset

from deepeval.dataset import EvaluationDataset
from deepeval.metrics import (
    ContextualRelevancyMetric,
    AnswerRelevancyMetric,
    FaithfulnessMetric,
)
from deepeval.test_case import LLMTestCase


class RAGEvaluator:
    def __init__(self, llm, respon, model, evaluate_ragas, evaluate_geval):
        self.llm = llm
        self.respon = respon
        self.model = model
        self.evaluate_ragas = evaluate_ragas
        self.evaluate_geval = evaluate_geval
        self.samples = self.create_samples()
        
    def create_samples(self):
        if str(self.respon["query"]["possible_options"]).lower() != "none":
            a = self.respon["code"]
        else:
            a = self.respon["answer"]
        ragas_sample = SingleTurnSample(
            user_input = self.respon["query"]["topic"],
            retrieved_contexts = self.respon["contexts"],
            response = a,
            # reference = self.ground_truth[i],
        )
        geval_sample = LLMTestCase(
            input = self.respon["query"]["topic"],
            actual_output = a,
            # expected_output = self.ground_truth[i],
            retrieval_context = self.respon["contexts"],
        )
        return {"ragas": [ragas_sample], "geval": [geval_sample]}

    def RAGAS(self):
        print("\nRAGAS evaluation")
        dataset = RagasEvaluationDataset(samples=self.samples["ragas"])
        evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model=self.model))
        evaluator_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings())
        
        metrics = [
            Faithfulness(llm=evaluator_llm),
            LLMContextPrecisionWithoutReference(llm=evaluator_llm),
            ResponseRelevancy(llm=evaluator_llm, embeddings=evaluator_embeddings),
        ]
        result = ragasEvaluate(dataset=dataset, metrics=metrics)

        dataframe = result.to_pandas()
        columns_to_include = dataframe.columns[3:] 
        result = [
            {col: row[col] for col in columns_to_include}
            for _, row in dataframe.iterrows()
        ]
        # obj = {"samples": result}
        # with open(f"ragas_result.json", 'w', encoding='utf-8') as file:
        #     json.dump(obj, file, ensure_ascii=False, indent=4)
        return result

    def DEEPEVAL(self):
        print("\nDEEPEVAL evaluation")
        metrics = [
            ContextualRelevancyMetric(threshold=0.5, model=self.model, include_reason=False, verbose_mode=False),
            AnswerRelevancyMetric(threshold=0.5, model=self.model, include_reason=False, verbose_mode=False),
            FaithfulnessMetric(threshold=0.5, model=self.model, include_reason=False, verbose_mode=False),
            ]
        dataset = EvaluationDataset(test_cases=self.samples["geval"])
        dataset_result = dataset.evaluate(metrics) 
        result = []
        for test_result in dataset_result.test_results:
            scores = {}
            for metric_data in test_result.metrics_data:
                scores[metric_data.name.lower().replace(" ", "_")] = metric_data.score
            result.append(scores)
        return result

    def evaluate(self):
        geval_result = self.DEEPEVAL() if self.evaluate_geval else [None]
        ragas_result = self.RAGAS() if self.evaluate_ragas else [None] 
        return {"ragas": ragas_result[0],"geval": geval_result[0]}
