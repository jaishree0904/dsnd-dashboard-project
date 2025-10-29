import matplotlib.pyplot as plt
import pandas as pd
from employee_events import QueryBase, Employee, Team
from utils import load_model

# Temporary replacement for missing fasthtml module
class H1:
    def __init__(self, text):
        self.text = f"<h1>{text}</h1>"

class Div:
    def __init__(self, content):
        self.content = f"<div>{content}</div>"

class FastHTML:
    def __init__(self, title, body):
        self.html = f"<html><head><title>{title}</title></head><body>{body}</body></html>"

    def render(self):
        return self.html


# Import QueryBase, Employee, Team from employee_events
from employee_events import QueryBase, Employee, Team

# import the load_model function from the utils.py file
from utils import load_model

"""
Below, we import the parent classes
you will use for subclassing
"""
from base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    MatplotlibViz,
    DataTable
)

from combined_components import FormGroup, CombinedComponent


# Create a subclass of base_components/dropdown called `ReportDropdown`
class ReportDropdown(Dropdown):
    
    def build_component(self, id, model):
        # Set the label attribute
        self.label = model.name
        # Call parent build_component
        return super().build_component(id, model)
    
    def component_data(self, model):
        # Use the model to get names and IDs
        return model.names()


# Create a subclass of base_components/BaseComponent called `Header`
class Header(BaseComponent):
    def build_component(self, id, model):
        # Return an H1 HTML element containing the model's name
        return H1(f"{model.name.title()} Report", cls="text-center text-2xl font-bold")


# Create a subclass of base_components/MatplotlibViz called `LineChart`
class LineChart(MatplotlibViz):

    def visualization(self, model, asset_id):
        df = model.event_counts(asset_id)
        df = df.fillna(0)
        df = df.set_index('event_date')
        df = df.sort_index()
        df = df.cumsum()
        df.columns = ['Positive', 'Negative']

        fig, ax = plt.subplots()
        df.plot(ax=ax)
        self.set_axis_styling(ax, border_color='black', font_color='black')

        ax.set_title(f"{model.name.title()} Event Trends")
        ax.set_xlabel("Date")
        ax.set_ylabel("Cumulative Events")

        return fig


# Create a subclass of base_components/MatplotlibViz called `BarChart`
class BarChart(MatplotlibViz):

    predictor = load_model()

    def visualization(self, model, asset_id):
        df = model.model_data(asset_id)
        probs = self.predictor.predict_proba(df)[:, 1]

        # Choose mean or first value based on model type
        if model.name == "team":
            pred = probs.mean()
        else:
            pred = probs[0]

        fig, ax = plt.subplots()
        ax.barh([''], [pred])
        ax.set_xlim(0, 1)
        ax.set_title('Predicted Recruitment Risk', fontsize=20)

        self.set_axis_styling(ax, border_color='black', font_color='black')
        return fig


# Create a subclass of combined_components/CombinedComponent called Visualizations
class Visualizations(CombinedComponent):
    children = [LineChart(), BarChart()]
    outer_div_type = Div(cls='grid')


# Create a subclass of base_components/DataTable called NotesTable
class NotesTable(DataTable):
    def component_data(self, model, entity_id):
        return model.notes(entity_id)


class DashboardFilters(FormGroup):
    id = "top-filters"
    action = "/update_data"
    method = "POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name='profile_type',
            hx_get='/update_dropdown',
            hx_target='#selector'
        ),
        ReportDropdown(
            id="selector",
            name="user-selection"
        )
    ]


# Create a subclass of CombinedComponents called Report
class Report(CombinedComponent):
    children = [
        Header(),
        DashboardFilters(),
        Visualizations(),
        NotesTable()
    ]


# Initialize a fasthtml app
app = FastHTML()

# Initialize the `Report` class
report = Report()


# Create a route for the root path
@app.get('/')
def home():
    return report(1, Employee())


# Route for employee ID
@app.get('/employee/{id}')
def employee(id: str):
    return report(id, Employee())


# Route for team ID
@app.get('/team/{id}')
def team(id: str):
    return report(id, Team())


# Keep the below code unchanged!
@app.get('/update_dropdown{r}')
def update_dropdown(r):
    dropdown = DashboardFilters.children[1]
    print('PARAM', r.query_params['profile_type'])
    if r.query_params['profile_type'] == 'Team':
        return dropdown(None, Team())
    elif r.query_params['profile_type'] == 'Employee':
        return dropdown(None, Employee())


@app.post('/update_data')
async def update_data(r):
    from fasthtml.common import RedirectResponse
    data = await r.form()
    profile_type = data._dict['profile_type']
    id = data._dict['user-selection']
    if profile_type == 'Employee':
        return RedirectResponse(f"/employee/{id}", status_code=303)
    elif profile_type == 'Team':
        return RedirectResponse(f"/team/{id}", status_code=303)


serve()
