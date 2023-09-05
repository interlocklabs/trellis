# write util function generate_data which takes in a voluptuous schema (for a dict)\
# and returns a dict which matches the schema

# this is how the input schema is set, from `Node`:
#     def set_input(self, input: dict[str:Any], wipe=True) -> None:
#         if not isinstance(input, dict):
#             raise ValueError(f"Input {input} is not a valid dict")
#         self.input = {**input, **self.input} if not wipe else input

# this is how the input schema is validated, from `Node`:
#     def validate_input(self) -> bool:
#         try:
#             return self._input_s(self.input)
#         except Invalid as e:
#             raise e