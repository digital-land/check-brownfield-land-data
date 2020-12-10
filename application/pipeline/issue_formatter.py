
class IssueFormatter():

    def extract_issue_data(issues):
        issues_by_row = {}
        for issue in issues:
            default_field = {
                issue['field']: {}
            }
            issues_by_row.setdefault(issue['row-number'], default_field)
            # print(f'{issue["field"]} : {issue["issue-type"]} : {issue["value"]}')
            issues_by_row[issue['row-number']].setdefault(issue['field'], {})
            # print(issues_by_row[issue['row-number']][issue['field']])
            issues_by_row[issue['row-number']][issue['field']][issue['issue-type']] = issue['value']
        return issues_by_row


    def map_issue(field, issue):
        keys = list(issue.keys())
        if "missing" in keys:
            return issue["missing"], "missing", f"No data for {field}"
        elif "enum" in keys:
            return issue["enum"], "invalid", f"Unexpected value for {field}"
        elif "outside England" in keys[0]:
            return issue[keys[0]], "invalid", f"Coordinate provided is outside England"
        elif "minimum" in keys:
            return issue[keys[0]], "invalid", f"Value provided is below the minimum allowed"
        elif "integer" in keys:
            return issue[keys[0]], "invalid", f"Value provided is not a valid number"
        elif "uri" in keys:
            return issue[keys[0]], "invalid", f"Value provided is not a valid URI"
        elif "decimal" in keys:
            return issue[keys[0]], "invalid", f"Unable to recognise coordinate"
        elif "date" in keys:
            return issue[keys[0]], "invalid", f"Date provided is not valid"
        elif "default" in keys:
            if field == 'LastUpdatedDate':
                return issue[keys[0]], "amended", f"No date provided for {field}. Setting to FirstAddedDate"
            elif field == 'NetDwellingsRangeTo':
                return issue[keys[0]], "amended", f"No value provided for {field}. Setting to NetDwellingsRangeFrom"
            elif field == 'OrganisationURI':
                return issue[keys[0]], "amended", f"No value provided for {field}. Setting to default for organisation."
            elif field == 'NetDwellingsRangeFrom':
                return issue[keys[0]], "amended", f"No value provided for {field}. Using value from deprecated MinNetDwellings column."
            else:
                return issue[keys[0]], "amended", f"No value provided for {field}. Setting to a default"
        else:
            return issue[keys[0]], keys[0], "some text"


    def generate_issue_message(field, issues):
        # 'Hectares': {'minimum': '0', 'missing': None}
        # 'SiteReference': {'missing': None}
        # empty defaults to stop it failing
        original = ""
        tag = ""
        message = ""

        issue_types = issues.keys()
        if len(issue_types) > 1:
            # can discount missing (is this done mistakenly?)
            if "missing" in issue_types:
                del issues['missing']
                original, tag, message = IssueFormatter.map_issue(field, issues)
            if "date" in issue_types and "default" in issue_types:
                original = issues['date']
                tag = "amended"
                message = f"Date provide is not a valid date. Set to default."
        else:
            # print(issues.keys())
            original, tag, message = IssueFormatter.map_issue(field, issues)
        return {
            "original": original,
            "tag": tag,
            "message": message
        }


    def split_coordinate(pt):
        #keys = list(issue.keys())
        #v = issue[keys[0]]
        coords = pt.split(",")
        return coords[0], coords[1]


    def coordinate_error_to_dict(v, message):
        return {
            "original": v,
            "tag": "invalid",
            "message": message
        }


    def format_issues_for_view(issues):
        for row in issues.keys():
            geox_issue = None
            for field in issues[row].keys():
                issues_with_field = issues[row][field]
                if field == "GeoX,GeoY":
                    keys = list(issues_with_field.keys())
                    x, y = IssueFormatter.split_coordinate(issues_with_field[keys[0]])
                    if "outside England" in keys[0]:
                        geox_issue = IssueFormatter.coordinate_error_to_dict(x, "Coordinate provided is outside England")
                        geoy_issue = IssueFormatter.coordinate_error_to_dict(y, "Coordinate provided is outside England")
                    elif "out of range" in keys[0]:
                        geox_issue = IssueFormatter.coordinate_error_to_dict(x, "Coordinate provided is not recognised")
                        geoy_issue = IssueFormatter.coordinate_error_to_dict(y, "Coordinate provided is not recognised")
                else:
                    issues[row][field] = IssueFormatter.generate_issue_message(field, issues_with_field)
            if geox_issue is not None:
                issues[row]['GeoX'] = geox_issue
                issues[row]['GeoY'] = geoy_issue
        return issues