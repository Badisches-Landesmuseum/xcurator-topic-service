from typing import List

'''
GraphQL Resolver Interface used for clean_text schema stiching
'''
class GraphQLResolver:

    def get_schemas(self) -> List:
        raise NotImplementedError("get_achemas is not implemented!")