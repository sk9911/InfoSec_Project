from datetime import date

visitation_document = {
    101:{
        'student_id': '2019A7PS0149G',
        'Scale_of_Health': 7, # 1-10 is considered
        'Duration_of_Rest_in_days': 10, # 1-60 is considered
        'Date_of_Visitation': date(2022, 3, 1)
    },
    102:{
        'student_id': '2019A7PS0150G',
        'Scale_of_Health': 9, # 1-10 is considered
        'Duration_of_Rest_in_days': 1, # 1-60 is considered
        'Date_of_Visitation': date(2022, 3, 1)
    },
    103:{
        'student_id': '2019A7PS0150G',
        'Scale_of_Health': 6, # 1-10 is considered
        'Duration_of_Rest_in_days': 3, # 1-60 is considered
        'Date_of_Visitation': date(2022, 3, 1)
    },
    104:{
        'student_id': '2019A7PS0152G',
        'Scale_of_Health': 4, # 1-10 is considered
        'Duration_of_Rest_in_days': 2, # 1-60 is considered
        'Date_of_Visitation': date(2022, 3, 1)
    },
}

verification_req_doc = {
    'date_of_Eval': date(2022, 3, 6),
    'threshold_lvl': 5, # 1-10 is considered
    'list_of_students': [(101,'2019A7PS0149G'),(102,'2019A7PS0150G'),(103,'2019A7PS0151G'),(104,'2019A7PS0152G'),(105,'2019A7PS0153G')]
}

def verify_visitation(verification_req_doc):
    makeup_granted = []
    for student in verification_req_doc['list_of_students']:
        if visitation_document.get(student[0]) == None:
            print("Student with ID {} is not present in the visitation document".format(student[1]))
        elif visitation_document.get(student[0])['student_id'] != student[1]:
            print("Student with ID {} is not matched with the entry in the visitation document".format(student[1]))
        elif visitation_document.get(student[0])['Scale_of_Health'] < verification_req_doc['threshold_lvl']:
            print("Student with ID {} is not granted the makeup bcoz of scale_of_health".format(student[1]))
        elif (verification_req_doc['date_of_Eval'] - visitation_document.get(student[0])['Date_of_Visitation']).days > visitation_document.get(student[0])['Duration_of_Rest_in_days']:
            print("Student with ID {} is not granted the makeup bcoz of date".format(student[1]))
        else:
            makeup_granted.append(student[1])
    return makeup_granted

if __name__ == "__main__":
    print(verify_visitation(verification_req_doc))




