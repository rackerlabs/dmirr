
import sys
from cement2.core import controller
from dmirr.cli.controllers.base import dMirrBaseController
from dmirr.core import exc

class ProjectController(dMirrBaseController):
    class meta:
        interface = controller.IController
        label = 'project'
        description = 'dMirr Project Resource Client Interface'
        arguments = [
            (['-l', '--label'], 
             dict(action='store', dest='label', metavar='STR',
                  help='project label (unique identifier)')),
            (['--display-name'], 
             dict(action='store', dest='display_name', metavar='TEXT',
                  help='project display name')),
            (['-d', '--desc'], 
             dict(action='store', dest='description', metavar='STR',
                  help='project description')),
            (['--private'], 
             dict(action='store', dest='private', metavar='STR',
                  help='privitization flag (boolean)')),
            (['-u', '--user'], 
             dict(action='store', dest='user', metavar='STR',
                  help='user label')),
            (['--url'], 
             dict(action='store', dest='url', metavar='URL',
                  help='full URL path')),
            (['project'], 
             dict(action='store', nargs='?',
                  help='project label to work with')), 
            ]
        defaults = {}

    @controller.expose(help="list all projects")
    def listall(self):
        response, data = self.conn.project.get()
        for project in data['objects']:
            print project['label']
            
    @controller.expose(help="display all project data")
    def show(self):
        try:
            assert self.app.pargs.project, "Project label required."
        except AssertionError, e:
            raise exc.dMirrArgumentError, e.args[0]
            
        response, data = self.conn.project.get(self.app.pargs.project)
        print data
            
    @controller.expose(help="create a new project")
    def create(self):
        try:
            assert self.app.pargs.user, "Project label required."
            assert self.app.pargs.user, "User label required."
        except AssertionError, e:
            raise exc.dMirrArgumentError, e.args[0]
            
        response, user = self.conn.user.get(self.app.pargs.user)
        if int(response['status']) == 404:
            raise exc.dMirrArgumentError("User '%s' does not exist." % \
                                     self.app.pargs.user)
        
        project = dict(
            label=self.app.pargs.label,
            display_name=self.app.pargs.display_name,
            description=self.app.pargs.description,
            private=self.app.pargs.private,
            owner=user['resource_uri'],
            )
            
        response, data = self.conn.project.create(params=project)
        if int(response['status']) != 201:
            print data['error_message']

        self.app.log.info("Project %s created." % self.app.pargs.label)
        
    @controller.expose(help="update an existing project")
    def update(self):
        response, project = self.conn.project.get(1)
        self.conn.project.update(project['id'], project)
        
        
    