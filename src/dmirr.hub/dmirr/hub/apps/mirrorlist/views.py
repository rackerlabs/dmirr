
import re
from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_page
from dmirr.hub.lib.geo import get_geodata_by_ip, get_distance
from dmirr.hub import db

def get_location(city=None, region=None, country=None):
    if city and region and country:
        location = "%s, %s %s" % (city, region, country)
    elif region and country:
        location = "%s %s" % (region, country)
    elif country:
        location = country
    else:
        location = 'US'
    return location

@cache_page(60 * 60)
def mirrorlist(request):
    data = {}
    resources = []
    client = get_geodata_by_ip(request.environ['REMOTE_ADDR'])
    repo = get_object_or_404(db.ProjectRepo, 
                             label=request.GET.get('repo', None))
    arch = get_object_or_404(db.Arch, 
                             label=request.GET.get('arch', None))
    protocol = get_object_or_404(db.Protocol, 
                             label=request.GET.get('protocol', 'http'))
    
    for resource in repo.project.resources.all():
        if not resource.include_in_mirrorlist:
            continue
        if protocol in resource.protocols.all() and \
           arch in repo.archs.all():
            full_uri = "%s://%s/%s/%s/" % (
                protocol.label, 
                resource.system.label,
                resource.path.strip('/'),
                re.sub('@arch@', arch.label, repo.path.strip('/')),
                )
            if not client:
                distance = 'unknown'
            else:
                distance = get_distance( 
                    (client['latitude'], client['longitude']), 
                    (resource.system.latitude, resource.system.longitude),
                    )
            resources.append((distance, full_uri, resource))
            
    resources.sort()
    if not client:
        data['location'] = 'Unknown Location'
    else:
        data['location'] = get_location(client.get('city', None), 
                                        client.get('region_name', None), 
                                        client.get('country_name', None))
    data['resources'] = resources
    return render(request, 'mirrorlist/list.html', data, 
                  content_type='text/plain')
