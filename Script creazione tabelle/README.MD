# Lista Tabelle Mongo
Contents [CREATE_AND_INSERT_CONTENT_TABLE]
ContentTags [CREATE_AND_INSERT_CONTENT_TABLE]
ContentMentions [CREATE_AND_INSERT_CONTENT_TABLE]
ContentBooked [CREATE_AND_INSERT_CONTENT_TABLE]
ContentDiscussion [CREATE_AND_INSERT_CONTENT_TABLE]
ContentLike [CREATE_AND_INSERT_CONTENT_TABLE]
DiscussionLike [CREATE_AND_INSERT_CONTENT_TABLE]
EventLocation [CREATE_AND_INSERT_CONTENT_TABLE]
EventMaps [CREATE_AND_INSERT_CONTENT_TABLE]
EventCoupon [CREATE_AND_INSERT_CONTENT_TABLE]
FollowUser [CREATE_AND_INSERT_FOLLOW_USER_AND_FOLLOW_USER_REQUEST]
FollowUserRequest [CREATE_AND_INSERT_FOLLOW_USER_AND_FOLLOW_USER_REQUEST]
Messages [CREATE_AND_INSERT_USER_MESSAGES]
ObjectMaps [CREATE_AND_INSERT_CONTENT_TABLE]
ObjectSeats [CREATE_AND_INSERT_CONTENT_TABLE]
PersonalDataRequest [CREATE_AND_INSERT_REQUEST_PERSONAL_DATA_TABLE]
SupportTickets [CREATE_AND_INSERT_SUPPORT_TICKET]
SupportTicketDiscussion [CREATE_AND_INSERT_SUPPORT_TICKET]
Tickets [CREATE_AND_INSERT_USER_TICKETS]
TicketReviews [CREATE_AND_INSERT_USER_TICKET_REVIEW]
Users [CREATE_AND_INSERT_USER_TABLE]
UserVerify [CREATE_AND_INSERT_USER_VERIFY_TABLE] 
UserSettings [CREATE_AND_INSERT_USER_SETTINGS]
UserCards [CREATE_AND_INSERT_USER_CARD]
UserAddresses [CREATE_AND_INSERT_USER_ADDRESSES]

# Campi Tabelle
Contents: {_id: MongoDB Id, n_group_id: number, t_alias_generated: string, t_caption:string, t_type: string, created_date:string, t_image_link:string, t_video_link:string, t_privacy:string, b_active:boolean, n_click: number, t_event_date:string}
ContentTags: {value: string, content_id: string }
ContentMentions: {value: string, content_id: string }
ContentBooked: { content_id: string, t_username: string, created_at: string }
ContentDiscussion: {"content_id": string, "parent_discussion_id": string, "body": string, "like_count": number, "t_alias_generated": string, "created_date": string, "t_alias_generated_reply": string}
DiscussionLike: { "content_id": string,"discussion_id": string,"t_username": string,"created_at": string }
ContentLike: { "content_id": string, "t_username": string, "created_at": string }
EventLocation: { "event_id": string //content_id, "t_address": string, "t_cap": number // > 9999 e < 100000, "t_city": string, "t_location_name": string, "t_province": string, "t_state": string }
EventMaps: {
    "t_map_name": string,
    "t_map_event_id": string,
    "t_map_type": //string però usa sempre "DISCOTECA" ,
    "t_map_num_column": number,
    "t_map_num_rows": number,
    "t_map_total_seat": number // è la moltiplicazione di num_column*num_rows
}
ObjectMaps: {
    "n_id_map": //_id della mappa inserita in EventMaps,
    "n_min_num_person": number,
    "n_max_num_person": number //deve essere >= di n_min_num_person,
    "n_limit_buy_for_person": number //deve essere compreso tra n_min_num_person e n_max_num_person,
    "n_object_price": number,
    "n_obj_map_cord_x": number //deve essere una riga valida es. se t_map_num_rows = 5, allora deve andare da 0 a 4,
    "n_obj_map_cord_y": number //deve essere una colonna valida es. se t_map_num_column = 4 allora deve andare da 0 a 3,
    "n_obj_map_cord_z": 1,
    "n_obj_map_width": number //max 240 min 80,
    "n_obj_map_height": number //max 100 min 40,
    "n_obj_map_text": string,
    "n_obj_map_fill": string //non obbligatorio e deve essere un colore in stile es #dfdfes,
    "t_note": string //non è obbligatorio,
    "t_type": // uno fra questi  OBJECT_MAP_TYPE {
    TABLE?: {
        DISCOTECA?: boolean;
        DISCOTECA_DJ?: boolean;
    },
    SEAT?: {
        TYPE: {
            NO_CONSUMATION?: boolean;
            WITH_CONSUMATION?: boolean;
        }
    }
}, //es {TABLE:{DISCOTECA:True}}
    "is_acquistabile": boolean
}
ObjectSeats: {
    "n_seat_num": number,
    "n_object_map_id": //_id del record inserito in ObjectMaps,
    "n_id_event": //content_id,
    "is_sell": boolean,
    "is_acquistabile": //is_acquistabile del record inserito in ObjectMaps
}
EventCoupon: {"event_id": string //content_id,"coupon_code": string,"discount": number //da 1 a 100}