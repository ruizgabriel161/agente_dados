from typing import override
from app.graph.context.context import Context
from app.graph.nodes.base_node import BaseNode
from app.graph.prompts.prompt import Supervisor
from app.graph.states.state import State
from langchain.chat_models import BaseChatModel
from langchain_core.messages import ToolMessage, HumanMessage, SystemMessage, BaseMessage




class CallNode(BaseNode):
    """Classe inicial que do grado"""
    def __init__(self, llm):
        super().__init__(llm)
      
    llm:BaseChatModel

    @override
    async def node_process(self, state: State, *, context: Context | None) -> State:
        '''
        Método abstraído da BaseNode usado para executar o node

        Args:
            state (State): State do grafico

        Returns:
            State: resultado da llm
        '''
        
        # print('>Call_Node')

        last_message:BaseMessage | ToolMessage | HumanMessage = state['messages'][-1]
        
        if isinstance(last_message, ToolMessage):
            prompt = await Supervisor('respose_sql').defined_prompt(result=last_message.text)
        else:
            prompt = await Supervisor('default').defined_prompt()

        llm_result = await self.llm.ainvoke([SystemMessage(prompt), *state['messages']])

        return {'messages': [llm_result]}
    
    @override
    def name(self) -> str:
        return 'call_node' 
        

    