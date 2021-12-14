
def abstract_token(target_node):

    if ":" in target_node:
        target_node, _ = target_node.split(":", 1)
    
    if target_node.strip() in ["(", ")", "[", "]", "{", "}", ",", ".", "\"", "\'", "="]: return "syntax"
    if len(target_node.strip()) == 0: return "indent"

    if target_node.strip() in ["+", "-", "*", "/", "//", "**", "%", 
                                "==", "!=", ">", "<", ">=", "<=",
                                "@", "is", "as", "and", "or", "not", "in"]:
        return "binary_operator_token"

    return target_node


class EditAbstraction:

    def __init__(self):
        self.node_to_type = {}

    def resolve_target(self, target):

        try:
            if target in self.node_to_type:
                return self.node_to_type[target]
        except TypeError:
            pass

        target_type = target[0]
        return abstract_token(target_type)

    def abstract_Insert(self, target, to_insert, position):

        insert_type = abstract_token(to_insert[0])
        
        if to_insert[-1] != "T": # It is not a token
            token_id   = to_insert[-1]
            self.node_to_type[token_id] = insert_type
        
        return "%s_to_%s" % (insert_type, target)

    def abstract_Update(self, target, update):
        return target

    def abstract_Delete(self, target):
        return target

    def abstract_Move(self, target, source, position):
        source = self.resolve_target(source)
        return "%s_to_%s" % (source, target)

    def abstract_op(self, operation):
        operator = operation[0]
        target   = self.resolve_target(operation[1])
        return operator, getattr(self, "abstract_%s" % operator)(target, *operation[2:])

    def __call__(self, edit_script):
        for operation in edit_script:
            yield self.abstract_op(operation)




# API version ------------------------------

def abstract_edit_script(edit_script):
    return EditAbstraction()(edit_script)