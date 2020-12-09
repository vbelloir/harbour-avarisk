# This Python file uses the following encoding: utf-8

# if __name__ == "__main__":
#     pass

import pyotherside
import threading
from datetime import datetime
from datetime import timezone
from datetime import timedelta
from urllib.request import urlopen

def getXmlAsElemT(url):

    with urlopen(url) as response:
        response_content = response.read()
    try:
        try:
            import xml.etree.cElementTree as ET
        except ImportError:
            import xml.etree.ElementTree as ET
        root = ET.fromstring(response_content.decode('utf-8'))
    except:
        # pyotherside.send('error')
        # print("Failed to parse xml from response (%s)" % traceback.format_exc())
        print('error')
    return root

def parse_xml(root, special):

    reports = []

    for bulletin in root.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}Bulletin'):
        # if elem.tag == '{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}Bulletin':
        report = avaReport()
        for detail in bulletin:
            # if 'locRef' in detail.tag:
                # report.validRegions.append(detail.attrib.get('{http://www.w3.org/1999/xlink}href'))
            for elem in detail.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}locRef'):
                report.validRegions.append(detail.attrib.get('{http://www.w3.org/1999/xlink}href'))
            for elem in detail.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}locRef'):
                report.validRegions.append(detail.attrib.get('{http://www.w3.org/1999/xlink}href'))
            for elem in detail.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}dateTimeReport'):
                report.repDate = tryparsedatetime(elem.text)
            for elem in detail.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}beginPosition'):
                report.timeBegin = tryparsedatetime(elem.text)
            for elem in detail.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}endPosition'):
                report.timeEnd = tryparsedatetime(elem.text)
            for elem in detail.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}DangerRating'):
                danger = elem
                mainValue = 0
                for dangDet in danger.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}mainValue'):
                    mainValue = int(dangDet.text)
                validElev = "-"
                for dangDet in danger.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validElevation'):
                    validElev = dangDet.attrib.get('{http://www.w3.org/1999/xlink}href')
                report.dangerMain.append({'mainValue':mainValue,'validElev':validElev})
            for elem in detail.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}DangerPattern'):
                pattern = elem
                for item in pattern.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}type'):
                    report.dangerPattern.append(item.text)
            i = 0
            for elem in detail.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}AvProblem'):
                problem = elem
                type = ""
                for item in problem.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}type'):
                    type = item.text
                aspect = []
                for item in problem.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validAspect'):
                    aspect.append(item.get('{http://www.w3.org/1999/xlink}href'))
                validElev = "-"
                for item in problem.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}validElevation'):
                    validElev = item.get('{http://www.w3.org/1999/xlink}href')
                i = i+1
                report.problemList.append({'type':type,'aspect':aspect,'validElev':validElev})
            for elem in detail.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}avActivityHighlights'):
                report.activityHighl = elem.text
            for elem in detail.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}avActivityComment'):
                report.activityCom = elem.text
            for elem in detail.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}snowpackStructureComment'):
                report.snowStrucCom = elem.text
            for elem in detail.iter(tag='{http://caaml.org/Schemas/V5.0/Profiles/BulletinEAWS}tendencyComment'):
                report.tendencyCom = elem.text
        reports.append(report)

    return reports


def getReports(url, special):
    root = getXmlAsElemT(url)
    reports = parse_xml(root, special)
    return reports


def tryparsedatetime(inStr):
    try:
        r_dateTime = datetime.strptime(inStr, '%Y-%m-%dT%XZ')
    except:
        try:
            r_dateTime = datetime.strptime(inStr[:19], '%Y-%m-%dT%X') # 2019-04-30T15:55:29+01:00
        except:
            print('some Error in try dateTime')
            r_dateTime = datetime.now()
    r_dateTime

    return r_dateTime


def issueReport(regionID, local):
    #urlTyrol = "https://api.avalanche.report/albina/api/bulletins"
    #urlKaernten = "www.lawine-kaernten.at/CAAML-XRISK-KTN.xml"
    url = "https://api.avalanche.report/albina/api/bulletins"
    reports = []
    provider = ""
    # Euregio-Region Tirol, Südtirol, Trentino
    if ("AT-07" in regionID) or ("AT-07" in regionID) or ("AT-07" in regionID):
        url = "https://api.avalanche.report/albina/api/bulletins"
        provider = "The displayed information is provided by an open data API on https://avalanche.report by: Avalanche Warning Service Tirol, Avalanche Warning Service Südtirol, Avalanche Warning Service Trentino."
        if "DE" in local.upper():
            url += "?lang=de"
            provider = "Die dargestellten Informationen werden über eine API auf https://avalanche.report abgefragt. Diese wird bereitgestellt von: Avalanche Warning Service Tirol, Avalanche Warning Service Südtirol, Avalanche Warning Service Trentino."

    # Kärnten
    if "AT-02" in regionID:
        url = "https://www.avalanche-warnings.eu/public/kaernten/caaml"
        provider = "Die dargestellten Informationen werden über eine API auf https://www.avalanche-warnings.eu abgefragt. Diese wird bereitgestellt vom: Lawinenwarndienst Kärnten."

    # Salzburg
    if "AT-05" in regionID:
        url = "https://www.avalanche-warnings.eu/public/salzburg/caaml/en"
        provider = "Die dargestellten Informationen werden über eine API auf https://www.avalanche-warnings.eu abgefragt. Diese wird bereitgestellt vom: Lawinenwarndienst Salzburg."
        if "DE" in local.upper():
            url = "https://www.avalanche-warnings.eu/public/salzburg/caaml"
            provider = "The displayed information is provided by an open data API on https://www.avalanche-warnings.eu by: Avalanche Warning Service Salzburg."

    reports.extend(getReports(url, ""))

    for report in reports:
        for ID in report.validRegions:
            if ID == regionID:
              matchingReport = report

    dangerLevel = 0
    for elem in matchingReport.dangerMain:
      if elem['mainValue'] > dangerLevel:
          dangerLevel = elem['mainValue']

    # for elem in matchingReport.problemList:
    #     elem['type'] = elem['type'].replace(' ', '_')


    LOCAL_TIMEZONE = datetime.now(timezone(timedelta(0))).astimezone().tzinfo

    pyotherside.send('dangerLevel', dangerLevel)
    pyotherside.send('dangerLevel_h', matchingReport.dangerMain[0]['mainValue'])
    if (len(matchingReport.dangerMain) > 1):
        pyotherside.send('dangerLevel_l', matchingReport.dangerMain[1]['mainValue'])
        pyotherside.send('dangerLevel_alti', matchingReport.dangerMain[0]['validElev'])
    else:
        pyotherside.send('dangerLevel_l', matchingReport.dangerMain[0]['mainValue'])
    pyotherside.send('highlights', matchingReport.activityHighl)
    pyotherside.send('comment',matchingReport.activityCom)
    pyotherside.send('structure', matchingReport.snowStrucCom)
    pyotherside.send('tendency', matchingReport.tendencyCom)
    pyotherside.send('repDate', matchingReport.repDate.astimezone(LOCAL_TIMEZONE))
    pyotherside.send('validFrom', matchingReport.timeBegin.astimezone(LOCAL_TIMEZONE))
    pyotherside.send('validTo', matchingReport.timeEnd.astimezone(LOCAL_TIMEZONE))
    pyotherside.send('numberOfDPatterns', len(matchingReport.problemList))
    pyotherside.send('dPatterns', str(matchingReport.problemList).replace("'", '"'))
    pyotherside.send('provider', provider)

    pyotherside.send('finished')

class Downloader:
    def __init__(self):
        self.bgthread = threading.Thread()
        self.bgthread.start()

    def download(self, regionID, local):
    # def download(self):
        if self.bgthread.is_alive():
            return
        self.bgthread = threading.Thread(target=issueReport(regionID, local))
        # self.bgthread = threading.Thread(target=getReportTyrol('IT-32-BZ-08'))
        self.bgthread.start()

class avaReport:
    def __init__(self):
        # self._items = []
        self.validRegions = []    # list of Regions
        self.repDate = ""         # Date of Report
        self.timeBegin = ""       # valid Ttime start
        self.timeEnd = ""         # valid time end
        self.dangerMain = []      # danger Value and elev
        self.dangerPattern = []   # list of Patterns
        self.problemList = []     # list of Problems with Sublist of Aspect&Elevation
        self.activityHighl = "none"   # String avalanche activity highlits text
        self.activityCom = "none"     # String avalanche comment text
        self.snowStrucCom = "none"    # String comment on snowpack structure
        self.tendencyCom = "none"     # String comment on tendency

downloader = Downloader()