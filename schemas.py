from marshmallow import Schema, fields, validate

class ItemSchema(Schema):
    # The ID is only for reading, not for creating
    id = fields.Int(dump_only=True)
    
    # Title must be a string, required, and between 1-100 characters
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    
    # Contents is optional
    contents = fields.Str(validate=validate.Length(max=500))
    
    # Priority must be one of these three options only
    priority = fields.Str(validate=validate.OneOf(["Low", "Medium", "High"]))
    
    # These are handled by the server, so they are read-only
    completed = fields.Bool(dump_only=True)
    created_at = fields.Str(dump_only=True)
    updated_at = fields.Str(dump_only=True)

# Create an instance to use in our routes
item_schema = ItemSchema()
items_schema = ItemSchema(many=True) # For lists of items