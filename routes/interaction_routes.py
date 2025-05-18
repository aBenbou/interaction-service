from flask import Blueprint, request, jsonify
from models.interaction import Interaction, Comment
from app import db
from ..validators import (
    InteractionCreate,
    InteractionUpdate,
    InteractionResponse,
    InteractionList,
    CommentCreate,
    CommentResponse
)
from pydantic import ValidationError
from datetime import datetime

# ... existing code ... 