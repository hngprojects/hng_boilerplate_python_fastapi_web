from typing import Optional
from fastapi import (
	APIRouter,
	Depends,
	Response,
	status,
	)
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.services.topic import topic_service
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.schemas.topic import TopicList, TopicUpdateSchema,TopicBase, TopicData, TopicSearchSchema, TopicDeleteSchema

topic = APIRouter(prefix='/help-center', tags=['Help-Center'])

@topic.get('/topics', response_model=TopicList)
async def retrieve_all_topics(
	db: Session = Depends(get_db)
):
	"""
	Description
		Get endpoint for unauthenticated users to to get all topics.

	Args:
		db: the database session object

	Returns:
		Response: a response object containing details if successful or appropriate errors if not
	"""	

	topics = topic_service.fetch_all(db=db)

	return success_response(
		status_code=status.HTTP_200_OK,
		message='Topics fetched successfully',
		data=jsonable_encoder(topics)
	)

@topic.get('/topics/{topic_id}', response_model=TopicData)
async def retrieve_topic(
    topic_id: str,
	db: Session = Depends(get_db)
):
	"""
	Description
		Get endpoint for unauthenticated users to to get a topic.

	Args:
		db: the database session object

	Returns:
		Response: a response object containing details if successful or appropriate errors if not
	"""	

	topic = topic_service.fetch(db=db, id=topic_id)

	return success_response(
		status_code=status.HTTP_200_OK,
		message='Topic fetched successfully',
		data=jsonable_encoder(topic)
	)

@topic.get('/search', response_model=TopicList)
async def search_for_topic(
	title: Optional[str] = None,
	content: Optional[str] = None,
	db: Session = Depends(get_db)
):
	"""
	Description
		Get endpoint for unauthenticated users to to search for topics.

	Args:
		db: the database session object

	Returns:
		Response: a response object containing details if successful or appropriate errors if not
	"""	
	topics = topic_service.search(db=db,title_query=title, content_query=content)

	return success_response(
		status_code=status.HTTP_200_OK,
		message='Topics fetched successfully',
		data=jsonable_encoder(topics)
	)

@topic.delete('/topics/{topic_id}')
async def delete_a_topic(
	topic_id: str,
	db: Session = Depends(get_db),
	current_user: User = Depends(user_service.get_current_super_admin),
):
	"""
	Description
		Delete endpoint for admin users to delete topics.

	Args:
		id: parameter for topic id
		db: the database session object

	Returns:
		Response: a response object containing details if successful or appropriate errors if not
	"""	

	topic_service.delete(db, topic_id)

	return Response(status_code=status.HTTP_204_NO_CONTENT)


@topic.patch("/topics/{topic_id}")
async def update_a_topic(
	topic_id: str,
	schema: TopicUpdateSchema,
	db: Session = Depends(get_db),
 	current_user: User = Depends(user_service.get_current_super_admin),
):
	"""
	Description
		Put endpoint for admin users to update a topic.

	Args:
		db: the database session object
		schema: TopicUpdateSchema
		id: parameter for topic id

	Returns:
		Response: a response object containing details if successful or appropriate errors if not
	"""	
	updated_topic = topic_service.update(db, schema, topic_id)
	return success_response(
		status_code=status.HTTP_200_OK,
		message='Topic updated successfully!',
		data=jsonable_encoder(updated_topic)
	)
	
@topic.post("/topics")
async def create_a_topic(
	schema: TopicBase,
	db: Session = Depends(get_db),
	current_user: User = Depends(user_service.get_current_super_admin),
):
	"""Endpoint to create a new topic."""
	"""
	Description
		Post endpoint for admin users to create a new topic.

	Args:
		db: the database session object
		schema: TopicUpdateSchema

	Returns:
		Response: a response object containing details if successful or appropriate errors if not
	"""	

	new_topic = topic_service.create(db, schema.title, schema.content, schema.tags)
	return success_response(
		status_code=status.HTTP_201_CREATED,
		message='Topic created successfully!',
  		data=jsonable_encoder(new_topic)
  	)
