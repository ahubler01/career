import streamlit as st
from st_aggrid import AgGrid
import pandas as pd
import re
from streamlit_gsheets import GSheetsConnection

# Center button and change labels
# Connect input db for selectbox
# Connect output db
# Improve questions
# Change buttons to labels



if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'Grid'

if 'current_step' not in st.session_state:
    st.session_state['current_step'] = 1

if 'queued_file' not in st.session_state:
    st.session_state['queued_file'] = 1

if 'all_answered' not in st.session_state:
    st.session_state['all_answered'] = False


#Hours per class

#Question, Mandatory field, Widget type, Format constraints
questionnaire_etudiant = {
    # Groupe 1 : Informations Générales
    "group_1": {
        "Informations Générales": {
            "email": {
                "label": "Quel est votre adresse électronique ?",
                "mandatory": True,
                "widget": "text_input",
                "format": r"^\S+@\S+\.\S+$",
            },
            "phone": {
                "label": "Quel est votre numéro de téléphone ?",
                "mandatory": False,
                "widget": "text_input",
                "format": r"^\+?\d{10,15}$",
            },
        }
    },
    "group_2": {
        "Établissement": {
            "region": {
                "label": "Dans quelle région est située ta formation ?",
                "mandatory": True,
                "widget": "selectbox",
                "format": "",
                "options": ["test"],
                "index": None,
            },
            "field_of_study": {
                "label": "Quelle est ta filière d'études ?",
                "mandatory": True,
                "widget": "selectbox",
                "format": "",
            },
            "study_program": {
                "label": "Nom de ta formation ?",
                "mandatory": True,
                "widget": "text_input",
                "format": "",
            }
        }
    },
    # Groupe 3 : Environnement Académique et Ressources
    "group_3": {
        "Environnement Académique et Ressources": {
            "main_subjects": {
                "label": "Quelles sont les principales matières étudiées dans ta formation ?",
                "mandatory": False,
                "widget": "multiselect",
                "format": "",
                "options": [
                            "Mathématiques", "Physique", "Chimie", "Biologie", "Géologie", "Statistiques",
                            "Génie Mécanique", "Génie Électrique", "Génie Civil", "Informatique", "Génie Chimique", "Robotique", "Génie des Matériaux",
                            "Médecine", "Infirmier(ère)", "Biologie Médicale", "Pharmacie", "Dentisterie", "Kinésithérapie",
                            "Psychologie", "Sociologie", "Histoire", "Géographie", "Sciences Politiques", "Anthropologie",
                            "Littérature", "Langues Étrangères", "Histoire de l'Art", "Philosophie", "Musique", "Arts Visuels",
                            "Économie", "Gestion d'Entreprise", "Marketing", "Comptabilité", "Finance", "Ressources Humaines",
                            "Droit Civil", "Droit Pénal", "Droit International", "Droit du Travail", "Droit Fiscal",
                            "Pédagogie", "Didactique", "Psychopédagogie", "Éducation Spéciale",
                            "Journalisme", "Communication", "Médias Numériques", "Relations Publiques"
                        ],
            },
            "teaching_balance": {
                "label": "Sur une échelle de 1 à 5, comment évalues-tu l'équilibre entre enseignement théorique et pratique ?",
                "mandatory": True,
                "widget": "slider",
                "format": r"^[1-5]$",
                "min": 1,
                "max": 5,
            },
            "support_services": {
                "label": "Ton établissement propose-t-il des services de soutien (tutorat, conseil, coaching) ?",
                "mandatory": True,
                "widget": "multiselect",
                "format": "",
                "options": [
                        "Tutorat académique",
                        "Conseil en orientation",
                        "Coaching personnel",
                        "Aide psychologique",
                        "Soutien pour les étudiants en situation de handicap",
                        "Ateliers de compétences d'étude",
                        "Mentorat",
                        "Soutien en langue étrangère",
                        "Aide à la rédaction et à la recherche",
                        "Ateliers de gestion du stress",
                        "Programmes de préparation aux examens",
                        "Conseils en carrière et placement professionnel",
                        "Aide financière et bourses d'étude",
                        "Activités de renforcement communautaire",
                        "Soutien aux étudiants internationaux"
                    ]
            },
            "admin_services": {
                "label": "Évalue sur une échelle de 1 à 5 la réactivité et l'efficacité des services administratifs.",
                "mandatory": True,
                "widget": "slider",
                "format": r"^[1-5]$",
                "min": 1,
                "max": 5,
            },
            "teacher_interaction": {
                "label": "Comment juges-tu l'interaction et la disponibilité des professeurs en dehors des cours sur une échelle de 1 à 5 ?",
                "mandatory": True,
                "widget": "slider",
                "format": r"^[1-5]$",
                "min": 1,
                "max": 5,
            },
            "student_collaboration": {
                "label": "Y a-t-il des initiatives pour encourager la collaboration entre étudiants ?",
                "mandatory": False,
                "widget": "selectbox",
                "format": "",
                "options": ["Oui", "Non"]
            }
        }
    },
    # Groupe 4 : Expérience et Engagement Étudiant
    "group_4": {
        "Expérience et Engagement Étudiant": {
            "specific_or_various_jobs": {
                "label": "Ta formation te prépare-t-elle à un métier spécifique ou à divers métiers ?",
                "mandatory": True,
                "widget": "selectbox",
                "format": "",
                "options": ["Métier spécifique", "Divers métier"]
            },
            "work_environment": {
                "label": "Sur une échelle de 1 à 5, évalue l'environnement de travail (1 pour Structuré, 5 pour Flexible).",
                "mandatory": True,
                "widget": "slider",
                "format": r"^[1-5]$",
                "min": 1,
                "max": 5
            },
            "class_size": {
                "label": "Combien d'étudiants comptent ta promotion ?",
                "mandatory": False,
                "widget": "selectbox",
                "format": "",  # Format numérique
                "options": [
                        "Moins de 10 étudiants",
                        "10 à 20 étudiants",
                        "20 à 30 étudiants",
                        "30 à 50 étudiants",
                        "50 à 100 étudiants",
                        "100 à 200 étudiants",
                        "200 à 300 étudiants",
                        "300 à 500 étudiants",
                        "500 à 1000 étudiants",
                        "Plus de 1000 étudiants"
                    ],
            },
            "public_speaking": {
                "label": "La prise de parole en public est-elle fréquente dans ta formation ?",
                "mandatory": False,
                "widget": "selectbox",
                "format": "",
                "options": [
                        "Très fréquente",
                        "Fréquente",
                        "Occasionnelle",
                        "Rare",
                        "Très rare",
                        "Pas du tout"
                    ]
            },
            "work_pace": {
                "label": "Sur une échelle de 1 à 5, évalue le rythme de travail (1 pour Lent, 5 pour Rapide).",
                "mandatory": True,
                "widget": "slider",
                "format": r"^[1-5]$",
                "min": 1,
                "max": 5,
            },
            "environment_type": {
                "label": "L'environnement est-il plutôt créatif ou technique ?",
                "mandatory": False,
                "widget": "selectbox",
                "format": "",
                "options": ["Créatif", "Technique"]
            },
            "internships_included": {
                "label": "Y a-t-il des stages inclus dans ta formation ?",
                "mandatory": True,
                "widget": "selectbox",
                "format": "",
                "options": ["Oui", "Non"]
            },
            "career_opportunities": {
                "label": "Peux-tu lister les principaux débouchés professionnels offerts par ta formation ?",
                "mandatory": False,
                "widget": "multiselect",
                "format": "",
                "options": [
                        "Enseignant / Professeur",
                        "Ingénieur",
                        "Chercheur scientifique",
                        "Médecin",
                        "Infirmier(ère)",
                        "Avocat",
                        "Comptable",
                        "Architecte",
                        "Psychologue",
                        "Consultant en management",
                        "Développeur de logiciels",
                        "Analyste de données",
                        "Designer graphique",
                        "Journaliste",
                        "Marketeur",
                        "Artiste",
                        "Musicien",
                        "Travailleur social",
                        "Entrepreneur",
                        "Responsable des ressources humaines",
                        "Agent de voyage",
                        "Chef cuisinier",
                        "Technicien de laboratoire",
                        "Pharmacien",
                        "Kinésithérapeute",
                        "Dentiste",
                        "Vétérinaire",
                        "Pilote",
                        "Traducteur / Interprète",
                        "Scientifique environnemental"
                    ]
            },
            "alignment_with_emerging_industries": {
                "label": "Ta formation est-elle en phase avec les industries émergentes ?",
                "mandatory": False,
                "widget": "multiselect",
                "format": "",
                "options": ["Oui", "Non"],
            },
            "community_project_initiatives": {
                "label": "Existe-t-il des initiatives pour encourager la participation à des projets communautaires ou de bénévolat ?",
                "mandatory": False,
                "widget": "selectbox",
                "format": "",
                "options": ["Oui", "Non"],
            },
            "research_project_opportunities": {
                "label": "Existe-t-il des opportunités pour s'impliquer dans des projets de recherche ou des concours académiques ?",
                "mandatory": False,
                "widget": "selectbox",
                "format": "",
                "options": ["Oui", "Non"],
            }
        }
    },
    # Groupe 5 : Diversité, Inclusion et Vie Campus
    "group_5": {
        "Diversité, Inclusion et Vie Campus": {
            "diversity_clubs": {
                "label": "Y a-t-il des clubs ou groupes dédiés à la promotion de la diversité culturelle ?",
                "mandatory": False,
                "widget": "selectbox",
                "format": "",
                "options": ["Oui", "Non"],
            },
            "disability_programs": {
                "label": "L'établissement propose-t-il des programmes pour l'intégration des étudiants en situation de handicap ?",
                "mandatory": False,
                "widget": "selectbox",
                "format": "",
                "options": ["Oui", "Non"],
            },
            "diversity_inclusion_training": {
                "label": "Existe-t-il des formations pour sensibiliser à la diversité et à l'inclusion ?",
                "mandatory": False,
                "widget": "radio",
                "format": "",
            },
            "sense_of_community": {
                "label": "Te sens-tu intégré(e) et faisant partie de la communauté étudiante ?",
                "mandatory": True,
                "widget": "selectbox",
                "format": "",
                "options": [
                        "Très intégré(e) et impliqué(e)",
                        "Plutôt intégré(e) et occasionnellement impliqué(e)",
                        "Moyennement intégré(e), avec quelques interactions",
                        "Peu intégré(e), rarement impliqué(e)",
                        "Pas du tout intégré(e), se sentant isolé(e)",
                        "Je ne cherche pas spécialement à m'intégrer"
                    ],
            },
            "housing_services": {
                "label": "L'établissement offre-t-il des services de logement ou d'aide à la recherche de logement ?",
                "mandatory": False,
                "widget": "multiselect",
                "format": "",
                "options": [
                        "Résidences universitaires sur le campus",
                        "Résidences universitaires hors campus",
                        "Aide à la recherche de logements privés",
                        "Partenariats avec des résidences étudiantes locales",
                        "Informations et conseils sur le logement",
                        "Subventions ou aides financières pour le logement",
                        "Aucun service de logement ou d'aide au logement proposé"
                    ]
            },
            "study_facilities_quality": {
                "label": "Sur une échelle de 1 à 5, évalue la qualité des laboratoires, bibliothèques et espaces d'étude.",
                "mandatory": True,
                "widget": "slider",
                "format": r"^[1-5]$",
                "min": 1,
                "max": 5
            },
            "student_accommodation_quality": {
                "label": "Si applicable, comment juges-tu la qualité de l'hébergement étudiant ? (Sur une échelle de 1 à 5)",
                "mandatory": False,
                "widget": "slider",
                "format": r"^[1-5]$",
                "min": 1,
                "max": 5
            },
            "campus_safety_accessibility": {
                "label": "Évalue sur une échelle de 1 à 5 la sécurité et l'accessibilité sur le campus.",
                "mandatory": True,
                "widget": "slider",
                "format": r"^[1-5]$",
                "min": 1,
                "max": 5
            }
        }
    },
    # Groupe 6 : Évaluation Globale de l'Expérience Étudiante
    "group_6": {
        "Évaluation Globale de l'Expérience Étudiante": {
            "overall_experience_rating": {
                "label": "Sur une échelle de 1 à 10, comment évalues-tu ton expérience globale en tant qu'étudiant dans cet établissement ?",
                "mandatory": True,
                "widget": "slider",
                "format": r"^[1-10]$",
                "min": 1,
                "max": 10
            },
            "satisfaction_with_choice": {
                "label": "Te sens-tu à l'aise dans ta formation et penses-tu avoir fait le bon choix ?",
                "mandatory": True,
                "widget": "selectbox",
                "format": "",
                "options": [
                        "Très à l'aise et complètement satisfait(e) de mon choix",
                        "Plutôt à l'aise et globalement satisfait(e)",
                        "Moyennement à l'aise, avec quelques doutes",
                        "Peu à l'aise et souvent en questionnement",
                        "Pas du tout à l'aise, je regrette mon choix",
                        "Indécis(e) / J'attends de voir comment les choses évoluent"
                    ]
            }
        }
    }
}

def set_page_view(page):
    st.session_state['current_view'] = page
    st.session_state['queued_file'] = None
    st.session_state['current_step'] = 1


def set_form_step(action, step=None):
    if action == 'Next':
        if st.session_state['all_answered']:
            st.session_state['current_step'] = st.session_state['current_step'] + 1
        else:
            st.error(f"Champ(s) obligatoire(s) manquant(s)")
    if action == 'Back':
        st.session_state['current_step'] = st.session_state['current_step'] - 1
    if action == 'Jump':
        st.session_state['current_step'] = step


##### wizard functions ####
def wizard_form_header():
    sf_header_cols = st.columns([1, 1.75, 1])

    with sf_header_cols[1]:
        st.subheader('Load Data to Snowflake')

    # determines button color which should be red when user is on that given step
    btn_1 = 'primary' if st.session_state['current_step'] == 1 else 'secondary'
    btn_2 = 'primary' if st.session_state['current_step'] == 2 else 'secondary'
    btn_3 = 'primary' if st.session_state['current_step'] == 3 else 'secondary'
    btn_4 = 'primary' if st.session_state['current_step'] == 4 else 'secondary'
    btn_5 = 'primary' if st.session_state['current_step'] == 5 else 'secondary'
    btn_6 = 'primary' if st.session_state['current_step'] == 6 else 'secondary'

    step_cols = st.columns([1, .75, .75, .75, .75, .75, 1])
    step_cols[1].button('1', on_click=set_form_step, args=['Jump', 1], type=btn_1)
    step_cols[2].button('2', on_click=set_form_step, args=['Jump', 2], type=btn_2)
    step_cols[3].button('3', on_click=set_form_step, args=['Jump', 3], type=btn_3)
    step_cols[4].button('4', on_click=set_form_step, args=['Jump', 4], type=btn_4)
    step_cols[5].button('5', on_click=set_form_step, args=['Jump', 5], type=btn_5)
    step_cols[6].button('6', on_click=set_form_step, args=['Jump', 6], type=btn_6)




### Replace Wizard Form Body with this ###
def wizard_form_body():
    def create_widget(question):
        widget_type = question['widget']
        if question['mandatory']:
            label = '*' + question['label']
        else:
            label = question['label']
        options = question.get('options', {})

        if widget_type == 'text_input':
            return st.text_input(label, **options)
        elif widget_type == 'number_input':
            return st.number_input(label, **options)
        elif widget_type == 'text_area':
            return st.text_area(label, **options)
        elif widget_type == 'slider':
            return st.slider(label, **options)
        elif widget_type == 'radio':
            return st.slider(label, **options)
        elif widget_type == 'selectbox':
            options = question.get('options', [])
            index = question.get('index', 0)
            return st.selectbox(label, options, index=index, key=label)
        elif widget_type == 'multiselect':
            options = question.get('options', [])
            index = question.get('index', 0)
            return st.selectbox(label, options, index=index, key=label)
        else:
            raise ValueError(f"Unsupported widget type: {widget_type}")

    def display_question(questions_group):
        st.session_state['all_answered'] = True
        for group, questions in questions_group.items():
            st.header(group)  # Replace with user-friendly group title
            st.markdown("_* Champ obligatoire_")
            for key, question in questions.items():
                value = create_widget(question)
                if value:
                    if (question.get('format') and not re.match(question['format'], str(value))):
                        st.error(f"Format non valide")
                        st.session_state['all_answered'] = False
                    else:
                        responses[key] = value
                elif not value and question['mandatory']:
                    st.session_state['all_answered'] = False
        return

    # st.write(st.session_state['current_step'])
    responses = {}
    if st.session_state['current_step'] == 1:
        questions_group = questionnaire_etudiant.get("group_1", {})
        responses['current_steps'] = display_question(questions_group)
    elif st.session_state['current_step'] == 2:
        questions_group = questionnaire_etudiant.get("group_2", {})
        responses['current_steps'] = display_question(questions_group)
    elif st.session_state['current_step'] == 3:
        questions_group = questionnaire_etudiant.get("group_3", {})
        responses['current_steps'] = display_question(questions_group)
    elif st.session_state['current_step'] == 4:
        questions_group = questionnaire_etudiant.get("group_4", {})
        responses['current_steps'] = display_question(questions_group)
    elif st.session_state['current_step'] == 5:
        questions_group = questionnaire_etudiant.get("group_5", {})
        responses['current_steps'] = display_question(questions_group)
    elif st.session_state['current_step'] == 6:
        questions_group = questionnaire_etudiant.get("group_6", {})
        responses['current_steps'] = display_question(questions_group)

                # else:
                #     if question['mandatory']:
                #         st.error(f"Champ obligatoire")

        return responses


def wizard_form_footer():
    form_footer_container = st.empty()
    with form_footer_container.container():
        # disable_back_button = True if st.session_state['current_step'] == 1 else False
        disable_next_button = True if st.session_state['current_step'] == 5 else False

        form_footer_cols = st.columns([5, 1, 1, 1.75])

        form_footer_cols[0].button('Cancel', on_click=set_page_view, args=['Grid'])
        # form_footer_cols[1].button('Back', on_click=set_form_step, args=['Back'], disabled=disable_back_button)
        form_footer_cols[3].button('Next', on_click=set_form_step, args=['Next'], disabled=disable_next_button)


        # file_ready = False if st.session_state['queued_file'] is not None else True
        # load_file = form_footer_cols[3].button('📤 Load Table', disabled=file_ready)

    ### Replace Render Wizard View With This ###


def render_wizard_view():
    with st.expander('', expanded=True):
        wizard_form_header()
        st.markdown('---')
        wizard_form_body()
        st.markdown('---')
        wizard_form_footer()


##### grid functions ####
def get_table_grid():
    data = {"Table Name": ["Product", "Employee", "Customer"], "Schema": ["Salesforce", "Salesforce", "Salesforce"],
            "Rows": [200, 300, 400]}
    df = pd.DataFrame(data=data)

    gridOptions = {
        "rowSelection": "single",
        "columnDefs": [
            {"field": "Table Name", "checkboxSelection": True},
            {"field": "Schema"},
            {"field": "Rows"}
        ]
    }

    return AgGrid(
        df,
        gridOptions=gridOptions,
        fit_columns_on_grid_load=True,
        theme="balham"
    )


def render_grid_view():
    st.header('Questionnaire orientation')
    user_type = st.radio(
        "Quel est votre rôle",
        ["Étudiants :male-student:", "Équipe pédagogique :male-teacher:", "Ancien étudiants :male-office-worker:"],
        index=None)
    user_type_selected = True if user_type is None else False

    # st.markdown(f"{user_type_selected}")
    st.button('Suivant', on_click=set_page_view, args=['Form'], disabled=user_type_selected, type='primary')


##### view rendering logic ####
if st.session_state['current_view'] == 'Grid':
    render_grid_view()
else:
    render_wizard_view()