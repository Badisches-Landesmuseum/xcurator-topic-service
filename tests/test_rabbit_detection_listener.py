import logging
import os
import sys
from datetime import datetime
from unittest import TestCase
#if 'topic_modeling_train' not in sys.path[0]:
 #   path = os.path.join(sys.path[0], 'topic_modeling_train')
  #  sys.path.insert(0, path)
from infrastructure.mongo_db import MongoDB

from infrastructure.model_setup import ModelSetup
from repositories.detection_result_repository import DetectionResultRepository

logging.info(os.path)

from messaging.detection_listener import TopicRabbitListener
from models.topic_result import TopicResult
from data_processing.data_matrix import DataMatrix
from data_processing.preprocessing.text_preprocessing import TextPreprocessing
from data_processing.handlers.text_handler import TextHandler
from py_config.application_config import YamlConfig
from data_processing.prediction_process import PredictionProcessClass
from models.xgboost import Xgboost
from models.lda import LDAModel
from data_processing.handlers.vector_handler import VectorHandler
from repositories.PickelRepository import PickelRepository
#from database.detection_result_repository import DetectionResultRepository
from infrastructure.rabbitmq import RabbitMQ
from rabbitmq_proto_lib.manager import RabbitManager
from repositories.PickelRepository import PickelRepository
from resolvers.topic_modeling_resolver import TopicModelingResolver


class TestTopicRabbitListener(TestCase):

    def test_seperate_accumulated(self):
        topics = [[0, [0, 1, 2, 3, 4, 5]], [1, [0, 1, 2, 3, 4, 5]], [2, [0, 1, 2, 3, 4, 5]], [3, [0, 1, 2, 3, 4, 5]]]
        topic_filtered, topic_document_filtered_accumulated = TopicRabbitListener.seperate_accumulated(self, topics)

        expected_accumulated = [[5], [5], [5], [5]]
        expected_topics = [[0, [0, 1, 2, 3, 4]], [1, [0, 1, 2, 3, 4]], [2, [0, 1, 2, 3, 4]], [3, [0, 1, 2, 3, 4]]]

        self.assertTrue(topic_document_filtered_accumulated == expected_accumulated)
        self.assertTrue(topic_filtered == expected_topics)

    def test_extract_topics(self):
        predictions_example = [[[0.020454100390140183,
                                 ['0.072*"bildung" ', ' 0.049*"betreuung" ', ' 0.045*"angebot" ', ' 0.029*"erziehung" ',
                                  ' 0.019*"zugang" ', ' 0.018*"bildungs" ', ' 0.017*"ausbau" ', ' 0.017*"qualitaet" ',
                                  ' 0.015*"unterschied" ', ' 0.013*"einrichtung" ', ' 0.012*"teilhabe" ',
                                  ' 0.011*"familie" ', '0.011*"autorengruppe" ', ' 0.010*"migrationshintergrund" ',
                                  ' 0.010*"bildungsberichterstattung" ', ' 0.010*"fachkraefte" ', ' 0.009*"laendern" ',
                                  ' 0.009*"zentrum" ', ' 0.009*"kindertagesbetreuung" ', ' 0.008*"bericht" ']],
                                [0.020453123109664222, ['0.106*"grafik" ', ' 0.048*"anzahl" ', ' 0.039*"einwohner" ',
                                                        ' 0.030*"woiwodschaft" ', ' 0.028*"selbstverwaltung" ',
                                                        ' 0.028*"kreisen" ', ' 0.022*"tabelle" ', ' 0.020*"ergebnis" ',
                                                        ' 0.018*"ebene" ', ' 0.017*"woiwodschaften" ',
                                                        ' 0.016*"gemeinde" ', ' 0.014*"selbstverwaltungswahlen" ',
                                                        ' 0.012*"kandidatinnen" ', ' 0.011*"bezirk" ',
                                                        ' 0.011*"liste" ', ' 0.010*"analyse" ',
                                                        ' 0.009*"zusammenhang" ', ' 0.009*"angelegenheit" ',
                                                        ' 0.008*"stadtpraesidenten" ', ' 0.008*"regelung" ']]], [2.]]
        topic_result_result_set = TopicResult(results=predictions_example)

        print(topic_result_result_set.results)

        pages = [[0, topic_result_result_set], [1, topic_result_result_set]]
        topic_document_extracted = TopicRabbitListener.extract_topics(self, pages)
        # result = [[0, [[['angebot', 'zugang', 'familie'], ['kreisen', 'ergebnis', 'ebene']], [], [], []]], [1, [[['angebot', 'zugang', 'familie'], ['kreisen', 'ergebnis', 'ebene']], [], [], []]]]
        result = [[0, [0.020454100390140183,
                       ['0.072*"bildung" ', ' 0.049*"betreuung" ', ' 0.045*"angebot" ', ' 0.029*"erziehung" ',
                        ' 0.019*"zugang" ', ' 0.018*"bildungs" ', ' 0.017*"ausbau" ', ' 0.017*"qualitaet" ',
                        ' 0.015*"unterschied" ', ' 0.013*"einrichtung" ', ' 0.012*"teilhabe" ', ' 0.011*"familie" ',
                        '0.011*"autorengruppe" ', ' 0.010*"migrationshintergrund" ',
                        ' 0.010*"bildungsberichterstattung" ', ' 0.010*"fachkraefte" ', ' 0.009*"laendern" ',
                        ' 0.009*"zentrum" ', ' 0.009*"kindertagesbetreuung" ', ' 0.008*"bericht" ']]], [1, [
            0.020454100390140183,
            ['0.072*"bildung" ', ' 0.049*"betreuung" ', ' 0.045*"angebot" ', ' 0.029*"erziehung" ', ' 0.019*"zugang" ',
             ' 0.018*"bildungs" ', ' 0.017*"ausbau" ', ' 0.017*"qualitaet" ', ' 0.015*"unterschied" ',
             ' 0.013*"einrichtung" ', ' 0.012*"teilhabe" ', ' 0.011*"familie" ', '0.011*"autorengruppe" ',
             ' 0.010*"migrationshintergrund" ', ' 0.010*"bildungsberichterstattung" ', ' 0.010*"fachkraefte" ',
             ' 0.009*"laendern" ', ' 0.009*"zentrum" ', ' 0.009*"kindertagesbetreuung" ', ' 0.008*"bericht" ']]]]
        self.assertTrue(topic_document_extracted == result)

    def test_listen(self):
        rabbit_service = TestTopicRabbitListener.setup_rabbit(self)
        page_1 = PageTest.__init__(self, 'deutete nichts Gutes. Wer würde ihm schon folgen, säpt in der Nacht und dazu noch in dieser engen Gasse mitten im übel beleum undeten Hafenviertel? Gerade jetzt, wo er das Ding seines Lebens gedreht </p> </p> hatte und mit der Beute verschwinden wollte! Hatte einer seiner zahllosen Kollegen dieselbe Idee gehabt, ihn beobachtet und abgewartet, um ihn nun um die Früchte seiner Arbeit zu erleichtern?')
        page_2 = ''
        body = BodyTest(id = '00', pages = [self, self],project_id = '0', document_id = '1', uploaded_time= datetime(2002, 12, 26))
        #TopicRabbitListener.listen(rabbit_service, self)
        self.assertTrue(True)

    def test_listen_2(self):
        rabbit_service = TestTopicRabbitListener.setup_rabbit(self)
        page_1 = PageTest(id='1', html='<p><span style="color: rgb(61,60,64);background-color: rgba(61,60,64,0.04);font-size: 13.5;font-family: Open Sans",</p><p> fly </p><p> </p><p>  sans-serif;">Jemand musste Josef K. verleumdet haben, denn ohne dass er etwas Böses getan hätte, wurde er eines Morgens verhaftet. »Wie ein Hund! « sagte er, es war, als sollte die Scham ihn überleben. Als Gregor Samsa eines Morgens aus unruhigen Träumen erwachte, fand er sich in seinem Bett zu einem ungeheueren Ungeziefer verwandelt. Und es war ihnen wie eine Bestätigung ihrer neuen Träume und guten Absichten, als am Ziele ihrer Fahrt die Tochter als erste sich erhob und ihren jungen Körper dehnte. »Es ist ein eigentümlicher Apparat«, sagte der Offizier zu dem <br>Forschungsreisenden und überblickte mit einem gewissermaßen bewundernden Blick den ihm doch wohlbekannten Apparat. Sie hätten noch ins Boot springen können, aber der Reisende hob ein schweres, geknotetes Tau vom Boden, drohte ihnen damit und hielt sie dadurch von dem Sprunge ab.<br>In den letzten Jahrzehnten ist das Interesse an Hungerkünstlern sehr zurückgegangen. Aber sie überwanden sich, umdrängten den Käfig und wollten sich gar nicht fortrühren. Jemand musste Josef K. verleumdet haben, denn ohne dass er etwas Böses getan hätte, wurde er eines Morgens verhaftet.<br>»Wie ein Hund! « sagte er, es war, als sollte die Scham ihn überleben. Als Gregor Samsa eines <br>Morgens aus unruhigen Träumen erwachte, fand er sich in seinem Bett zu einem ungeheueren <br>Ungeziefer verwandelt. Und es war ihnen wie eine Bestätigung ihrer neuen Träume und guten Absichten, als am Ziele ihrer Fahrt die Tochter als erste sich erhob und ihren jungen Körper dehnte. <br>»Es ist ein eigentümlicher Apparat«, sagte der Offizier zu dem Forschungsreisenden und überblickte mit einem gewissermaßen bewundernden Blick den ihm doch wohlbekannten Apparat.<br>Sie hätten noch ins Boot springen können, aber der Reisende hob ein schweres, geknotetes Tau vom Boden, drohte ihnen damit und hielt sie dadurch von dem Sprunge ab. In den letzten Jahrzehnten ist das Interesse an Hungerkünstlern sehr zurückgegangen. Aber sie überwanden sich, umdrängten den Käfig und wollten sich gar nicht fortrühren. Jemand musste Josef K. verleumdet haben, denn ohne dass er etwas Böses getan hätte, wurde er eines Morgens verhaftet. »Wie ein Hund! « sagte er, es war, als sollte die Scham ihn überleben. Als Gregor Samsa eines Morgens aus unruhigen Träumen erwachte, fand er sich in seinem Bett zu einem ungeheueren Ungeziefer verwandelt. Und es war ihnen wie eine Bestätigung ihrer neuen Träume und guten Absichten, als am Ziele ihrer Fahrt die Tochter als erste sich erhob und ihren jungen Körper dehnte.<br>»Es ist ein eigentümlicher Apparat«, sagte der Offizier zu dem Forschungsreisenden und überblickte mit einem gewissermaßen bewundernden Blick den ihm doch wohlbekannten Apparat. Sie hätten noch ins Boot springen können, aber der Reisende hob ein schweres, geknotetes Tau vom Boden, drohte ihnen damit und hielt sie dadurch von dem Sprunge ab. In den letzten Jahrzehnten ist das Interesse an Hungerkünstlern sehr zurückgegangen. Aber sie überwanden sich, umdrängten den Käfig und wollten sich gar nicht fortrühren. Jemand musste Josef K. verleumdet haben, denn ohne dass er etwas Böses getan hätte, wurde er eines Morgens verhaftet. »Wie ein Hund! « sagte er, es war, als sollte die Scham ihn überleben. Als Gregor Samsa eines Morgens aus unruhigen Träumen erwachte, fand er sich in seinem Bett zu einem ungeheueren Ungeziefer verwandelt.<br>Und es war ihnen wie eine Bestätigung ihrer neuen Träume und guten Absichten, als am Ziele ihrer <br>Fahrt die Tochter als erste sich erhob und ihren jungen Körper dehnte. »Es ist ein eigentümlicher Apparat«, sagte der Offizier zu dem Forschungsreisenden und überblickte mit einem gewissermaßen bewundernden Blick den ihm doch wohlbekannten Apparat. Sie hätten noch ins Boot springen können, aber der Reisende hob ein schweres, geknotetes Tau vom Boden, drohte ihnen damit und hielt sie dadurch von dem Sprunge ab. In den letzten Jahrzehnten ist das Interesse an Hungerkünstlern sehr zurückgegangen. Aber sie überwanden sich, umdrängten den Käfig und wollten sich gar nicht fortrühren. Jemand musste Josef K. verleumdet haben, denn ohne dass er etwas Böses getan hätte, wurde er eines Morgens verhaftet. »Wie ein Hund! « sagte er, es war, als sollte die Scham ihn überleben. Als Gregor Samsa eines Morgens aus unruhigen Träumen erwachte, fand er sich in seinem Bett zu einem ungeheueren Ungeziefer verwandelt. Und es war ihnen wie eine Bestätigung ihrer neuen Träume und guten Absichten, als am Ziele ihrer Fahrt die Tochter als erste sich erhob und ihren jungen Körper dehnte. »Es ist ein eigentümlicher Apparat«, sagte der Offizier zu dem Forschungsreisenden und überblickte mit einem gewissermaßen bewundernden <br>Blick den ihm doch wohlbekannten Apparat. Sie hätten noch ins Boot springen können, aber der Reisende hob ein schweres, geknotetes Tau vom Boden, drohte ihnen damit und hielt sie dadurch von dem Sprunge ab. In den letzten Jahrzehnten ist das Interesse an Hungerkünstlern sehr zurückgegangen. Aber sie überwanden sich, umdrängten den Käfig und wollten sich gar nicht fortrühren. Jemand musste Josef K. verleumdet haben, denn ohne dass er etwas Böses getan hätte, wurde er eines Morgens verhaftet. »Wie</span></p>')
        page_2 = PageTest2(id='2', html='<p>n jungen Körper dehnte. »Es ist ein eigentümlicher Apparat«, sagte der Offizier zu dem Forsch </p>')
        page_3 = PageTest2(id='2', html='<p></p><p>Jemand musste Josef K. verleumdet haben, denn ohne dass er etwas Böses getan hätte, wurde er eines Morgens verhaftet. »Wie ein Hund! « sagte er, es war, als sollte die Scham ihn überleben. Als Gregor Samsa eines Morgens aus unruhigen Träumen erwachte, fand er sich in seinem Bett zu einem ungeheueren Ungeziefer verwandelt. Und es war ihnen wie eine Bestätigung ihrer neuen Träume und guten Absichten, als am Ziele ihrer Fahrt die Tochter als erste sich erhob und ihren jungen Körper dehnte. »Es ist ein eigentümlicher Apparat«, sagte der Offizier zu dem Forschungsreisenden und überblickte mit einem gewissermaßen bewundernden Blick den ihm doch wohlbekannten Apparat. Sie hätten noch ins Boot springen können, aber der Reisende hob ein schweres, geknotetes Tau vom Boden, drohte ihnen damit und hielt sie dadurch von dem Sprunge ab. </p><p>In den letzten Jahrzehnten ist das Interesse an Hungerkünstlern sehr zurückgegangen. Aber sie überwanden sich, umdrängten den Käfig und wollten sich gar nicht fortrühren. Jemand musste Josef K. verleumdet haben, denn ohne dass er etwas Böses getan hätte, wurde er eines Morgens verhaftet. »Wie ein Hund! « sagte er, es war, als sollte die Scham ihn überleben. Als Gregor Samsa eines Morgens aus unruhigen Träumen erwachte, fand er sich in seinem Bett zu einem ungeheueren Ungeziefer verwandelt. Und es war ihnen wie eine Bestätigung ihrer neuen Träume und guten Absichten, als am Ziele ihrer Fahrt die Tochter als erste sich erhob und ihren jungen Körper dehnte. »Es ist ein eigentümlicher Apparat«, sagte der Offizier zu dem Forschungsreisenden und überblickte mit einem gewissermaßen bewundernden Blick den ihm doch wohlbekannten Apparat. </p> <p>Sie hätten noch ins Boot springen können, aber der Reisende hob ein schweres, geknotetes Tau vom Boden, drohte ihnen damit und hielt sie dadurch von dem Sprunge ab. In den letzten Jahrzehnten ist das Interesse an Hungerkünstlern sehr zurückgegangen. Aber sie überwanden sich, umdrängten den Käfig und wollten sich gar nicht fortrühren. Jemand musste Josef K. verleumdet haben, denn ohne dass er etwas Böses getan hätte, wurde er eines Morgens verhaftet. »Wie ein Hund! « sagte er, es war, als sollte die Scham ihn überleben. Als Gregor Samsa eines Morgens aus unruhigen Träumen erwachte, fand er sich in seinem Bett zu einem ungeheueren Ungeziefer verwandelt. Und es war ihnen wie eine Bestätigung ihrer neuen Träume und guten Absichten, als am Ziele ihrer Fahrt die Tochter als erste sich erhob und ihren jungen Körper dehnte. </p> <p>»Es ist ein eigentümlicher Apparat«, sagte der Offizier zu dem Forschungsreisenden und überblickte mit einem gewissermaßen bewundernden Blick den ihm doch wohlbekannten Apparat. Sie hätten noch ins Boot springen können, aber der Reisende hob ein schweres, geknotetes Tau vom Boden, drohte ihnen damit und hielt sie dadurch von dem Sprunge ab. In den letzten Jahrzehnten ist das Interesse an Hungerkünstlern sehr zurückgegangen. Aber sie überwanden sich, umdrängten den Käfig und wollten sich gar nicht fortrühren. Jemand musste Josef K. verleumdet haben, denn ohne dass er etwas Böses getan hätte, wurde er eines Morgens verhaftet. »Wie ein Hund! « sagte er, es war, als sollte die Scham ihn überleben. Als Gregor Samsa eines Morgens aus unruhigen Träumen erwachte, fand er sich in seinem Bett zu einem ungeheueren Ungeziefer verwandelt. </p> <p>Und es war ihnen wie eine Bestätigung ihrer neuen Träume und guten Absichten, als am Ziele ihrer Fahrt die Tochter als erste sich erhob und ihren jungen Körper dehnte. »Es ist ein eigentümlicher Apparat«, sagte der Offizier zu dem Forschungsreisenden und überblickte mit einem gewissermaßen bewundernden Blick den ihm doch wohlbekannten Apparat. Sie hätten noch ins Boot springen können, aber der Reisende hob ein schweres, geknotetes Tau vom Boden, drohte ihnen damit und hielt sie dadurch von dem Sprunge ab. In den letzten Jahrzehnten ist das Interesse an Hungerkünstlern sehr zurückgegangen. Aber sie überwanden sich, umdrängten den Käfig und wollten sich gar nicht fortrühren. Jemand musste Josef K. verleumdet haben, denn ohne dass er etwas Böses getan hätte, wurde er eines Morgens verhaftet. »Wie ein Hund! « sagte er, es war, als sollte die Scham ihn überleben. Als Gregor Samsa eines Morgens aus unruhigen Träumen erwachte, fand er sich in seinem Bett zu einem ungeheueren Ungeziefer verwandelt. Und es war ihnen wie </p> <p></p>')
        page_4 = PageTest2(id='2', html='<p></p> <p>eine Bestätigung ihrer neuen Träume und guten Absichten, als am Ziele ihrer Fahrt die Tochter als erste sich erhob und ihren jungen Körper dehnte. »Es ist ein eigentümlicher Apparat«, sagte der Offizier zu dem Forschungsreisenden und überblickte mit einem gewissermaßen bewundernden Blick den ihm doch wohlbekannten Apparat. Sie hätten noch ins Boot springen können, aber der Reisende hob ein schweres, geknotetes Tau vom Boden, drohte ihnen damit und hielt sie dadurch von dem Sprunge ab. In den letzten Jahrzehnten ist das Interesse an Hungerkünstlern sehr zurückgegangen. Aber sie überwanden sich, umdrängten den Käfig und wollten sich gar nicht fortrühren. Jemand musste Josef K. verleumdet haben, denn ohne dass er etwas Böses getan hätte, wurde er eines Morgens verhaftet. »Wie</p> <p></p>')
        body = BodyTest(id = '007', pages = [page_1, page_2, page_3, page_4],project_id = '606ee5bf6769f83e24dc16cc', document_id = '111', uploaded_time= datetime(2002, 12, 26) )
        print(body)
        rabbit_service.on_message(body, message='')
        self.assertTrue(True)

    def test_listen_3(self):
        rabbit_service = TestTopicRabbitListener.setup_rabbit(self)
        #page_1 = PageTest('<h1 class="title">Regensburg wird mit Siemens nachhaltigen öffentlichen Nahverkehr vorantreiben </h1> \n<p></p> \n<p>• Ausstattung des Busdepots mit Lade- und Energieverteilungstechnik</p> \n<p>• 23 Ladestationen versorgen eBusse mit je 150kW</p> \n<p>• Einfache Installation der Energieverteilung im bestehenden Gebäude durch Einsatz von Stromschienen </p> \n<p></p> \n<p>Siemens Smart Infrastructure erhielt von den Regensburger Verkehrsbetrieben „das </p> \n<p>Stadtwerk Regensburg.Mobilität GmbH“ den Auftrag, das Busdepot in der Markomannenstraße für den Umstieg auf Elektromobilität auszurüsten. Siemens wird dafür sowohl die Ladeinfrastruktur als auch die Stromversorgungstechnik liefern. Die Inbetriebnahme ist für 2021 geplant. Bereits seit 2017 verkehren in Regensburg die ersten Elektrobusse im Innenstadtbereich. </p> \n<p></p> \n<p>„Um den Verkehr in Regensburg weiterhin umweltverträglicher und klimaneutral zu gestalten, wollen wir die Elektrifizierung des Öffentlichen Personennahverkehrs weiter vorantreiben“, sagte Manfred Koller Geschäftsführer von „das </p> \n<p>Stadtwerk.Regensburg“. „Für uns ist es wichtig, die neue Ladeinfrastruktur einfach und wirtschaftlich in das bestehende Busdepot zu integrieren. Außerdem soll die Möglichkeit bestehen, die Halle künftig mit weiteren Lademöglichkeiten zu bestücken. Siemens hat uns hier nicht nur mit der einfach zu erweiternden Ladeinfrastruktur überzeugt, sondern auch mit dem Schienenverteilersystem zur Stromverteilung als Alternative zu einer aufwändigen Verkabelung.“ </p> \n<p></p> \n<p>Mit den Ladestationen vom Typ Sicharge UC 200 können künftig 22 neue Elektrobusse an 23 Stellplätzen mit einer Ladeleistung von je 150 kW versorgt werden. Dies geschieht entweder über Nacht oder während anderer betrieblicher </p> \n<p>Aufenthaltszeiten über Ladekabel und Stecker. An 16 der 23 Plätze kommt eine </p> \n<p>besondere Kabelrolle zum Einsatz, bei der das Kabel nach Abschluss des Ladevorgangs automatisch aufgerollt wird. Die Durchfahrwege bleiben dadurch frei. </p> \n<p>Betrieben werden die Fahrzeuge mit Ökostrom des Energieversorgers im Regensburger Unternehmensverbund, der REWAG. Dieser wird lokal und regenerativ erzeugt. </p> \n<p>„Dieses Projekt zeigt wieder einmal, wie wichtig es ist, die neue Ladeinfrastruktur in bestehende Gebäude integrieren zu können. Viele Städte investieren in nachhaltigen Busverkehr, dennoch soll der Umstieg so wirtschaftlich wie möglich erfolgen. Bestehende Depots müssen deshalb einfach und kostengünstig auf eBus-</p> \n<p>Betrieb umgerüstet werden,“ sagte Birgit Dargel, Leiterin Future Grids bei Siemens Smart Infrastructure. </p> \n<p></p> \n<p>Um das Depot an das öffentliche Stromnetz anzuschließen und den Strom im Gebäude weiter zu verteilen, installiert Siemens zudem Transformatoren und eine Sivacon S8 Niederspannungsschaltanlage. </p> \n<p>Über ein Stromschienensystem vom Typ Sivacon 8PS werden die einzelnen Ladestationen dann innerhalb des Depots mit Energie versorgt. Das Besondere an dieser Form der Energieverteilung: Über spezielle Verbindungsstücke lassen sich Stromschienen den Gegebenheiten des bestehenden Gebäudes einfach anpassen. </p> \n<p>Sie sind damit flexibler als Leitungen, leichter und schneller zu installieren. Über </p> \n<p>Abgangskästen können bei Bedarf weitere Verbraucher hinzugefügt werden. Bei der Planung der Energieverteilung wird mit Hilfe von digitalen Planungstools ein digitaler Zwilling des Schienenverteilersystems erstellt. Eine künftige modulare Erweiterung des Systems kann damit simuliert und schon heute in den Planungsprozess einbezogen werden. Dies ermöglicht eine vorausschauende und wirtschaftliche Planung sowie eine effiziente Ausführung. </p> \n<p></p> \n<p>Diese Presseinformation sowie Pressebilder finden Sie unter https://sie.ag/36SrL71</p> \n<p></p> \n<p>Weitere Informationen zu Siemens Smart Infrastructure finden Sie unter www.siemens.com/smartinfrastructure </p> \n<p>Informationsnummer: HQSIPR202102026123DE</p> \n<p>Siemens AG Presseinformation </p> \n<p>Weitere Informationen zum Ladesystem Sicharge UC finden Sie unter www.siemens.de/sichargeuc</p>')
        page_1 = PageTest(id='1', html='<p></p> \n<p>Regensburg wird mit Siemens nachhaltigen öffentlichen Nahverkehr vorantreiben </p> \n<p>• Ausstattung des Busdepots mit Lade- und Energieverteilungstechnik </p> \n<p>• 23 Ladestationen versorgen eBusse mit je 150kW </p> \n<p>• Einfache Installation der Energieverteilung im bestehenden Gebäude durch Einsatz von </p> \n<p>Stromschienen </p> \n<p> </p> \n<p>Siemens Smart Infrastructure erhielt von den Regensburger Verkehrsbetrieben „das </p> \n<p>Stadtwerk Regensburg.Mobilität GmbH“ den Auftrag, das Busdepot in der Markomannenstraße für </p> \n<p>den Umstieg auf Elektromobilität auszurüsten. Siemens wird dafür sowohl die Ladeinfrastruktur als </p> \n<p>auch die Stromversorgungstechnik liefern. Die Inbetriebnahme ist für 2021 geplant. Bereits seit 2017 </p> \n<p>verkehren in Regensburg die ersten Elektrobusse im Innenstadtbereich. </p> \n<p> </p> \n<p>„Um den Verkehr in Regensburg weiterhin umweltverträglicher und klimaneutral zu gestalten, wollen </p> \n<p>wir die Elektrifizierung des Öffentlichen Personennahverkehrs weiter vorantreiben“, sagte Manfred </p> \n<p>Koller Geschäftsführer von „das </p> \n<p>Stadtwerk.Regensburg“. „Für uns ist es wichtig, die neue Ladeinfrastruktur einfach und wirtschaftlich </p> \n<p>in das bestehende Busdepot zu integrieren. Außerdem soll die Möglichkeit bestehen, die Halle </p> \n<p>künftig mit weiteren Lademöglichkeiten zu bestücken. Siemens hat uns hier nicht nur mit der einfach </p> \n<p>zu erweiternden Ladeinfrastruktur überzeugt, sondern auch mit dem Schienenverteilersystem zur </p> \n<p>Stromverteilung als Alternative zu einer aufwändigen Verkabelung.“ </p> \n<p> </p> \n<p>Mit den Ladestationen vom Typ Sicharge UC 200 können künftig 22 neue Elektrobusse an 23 </p> \n<p>Stellplätzen mit einer Ladeleistung von je 150 kW versorgt werden. Dies geschieht entweder über </p> \n<p>Nacht oder während anderer betrieblicher </p> \n<p>Aufenthaltszeiten über Ladekabel und Stecker. An 16 der 23 Plätze kommt eine </p> \n<p>besondere Kabelrolle zum Einsatz, bei der das Kabel nach Abschluss des Ladevorgangs automatisch </p> \n<p>aufgerollt wird. Die Durchfahrwege bleiben dadurch frei. </p> \n<p>Betrieben werden die Fahrzeuge mit Ökostrom des Energieversorgers im Regensburger </p> \n<p>Unternehmensverbund, der REWAG. Dieser wird lokal und regenerativ erzeugt. </p> \n<p></p>')
        page_2 = PageTest(id='2', html='<p></p> \n<p>„Dieses Projekt zeigt wieder einmal, wie wichtig es ist, die neue Ladeinfrastruktur in bestehende </p> \n<p>Gebäude integrieren zu können. Viele Städte investieren in nachhaltigen Busverkehr, dennoch soll </p> \n<p>der Umstieg so wirtschaftlich wie möglich erfolgen. Bestehende Depots müssen deshalb einfach und </p> \n<p>kostengünstig auf eBus- </p> \n<p>Betrieb umgerüstet werden,“ sagte Birgit Dargel, Leiterin Future Grids bei Siemens Smart </p> \n<p>Infrastructure. </p> \n<p> </p> \n<p>Um das Depot an das öffentliche Stromnetz anzuschließen und den Strom im Gebäude weiter zu </p> \n<p>verteilen, installiert Siemens zudem Transformatoren und eine Sivacon S8 </p> \n<p>Niederspannungsschaltanlage. </p> \n<p>Über ein Stromschienensystem vom Typ Sivacon 8PS werden die einzelnen Ladestationen dann </p> \n<p>innerhalb des Depots mit Energie versorgt. Das Besondere an dieser Form der Energieverteilung: </p> \n<p>Über spezielle Verbindungsstücke lassen sich Stromschienen den Gegebenheiten des bestehenden </p> \n<p>Gebäudes einfach anpassen. </p> \n<p>Sie sind damit flexibler als Leitungen, leichter und schneller zu installieren. Über </p> \n<p>Abgangskästen können bei Bedarf weitere Verbraucher hinzugefügt werden. Bei der Planung der </p> \n<p>Energieverteilung wird mit Hilfe von digitalen Planungstools ein digitaler Zwilling des </p> \n<p>Schienenverteilersystems erstellt. Eine künftige modulare Erweiterung des Systems kann damit </p> \n<p>simuliert und schon heute in den Planungsprozess einbezogen werden. Dies ermöglicht eine </p> \n<p>vorausschauende und wirtschaftliche Planung sowie eine effiziente Ausführung. </p> \n<p> </p> \n<p>Diese Presseinformation sowie Pressebilder finden Sie unter https://sie.ag/36SrL71 </p> \n<p> </p> \n<p>Weitere Informationen zu Siemens Smart Infrastructure finden Sie unter </p> \n<p>www.siemens.com/smartinfrastructure </p> \n<p>Informationsnummer: HQSIPR202102026123DE </p> \n<p>Siemens AG Presseinformation </p> \n<p>Weitere Informationen zum Ladesystem Sicharge UC finden Sie unter www.siemens.de/sichargeuc </p> \n<p></p>')

        #606ee5bf6769f83e24dc16cc
        body = BodyTest(id = 'hall12ja', pages = [page_1, page_2],project_id = '61a4fb440f3e9e00355c4c3f', document_id = 'hisa1', uploaded_time= datetime(2002, 12, 26) )
        print(body)
        res = TopicRabbitListener.on_message(rabbit_service, body, message='')
        print(res)
        self.assertTrue(True)


    def setup_rabbit(self):
        '''   model_path_conf = '/topic_modeling/resources/models/bpb-topic-modeling-conf'
        model_path = '/topic_modeling/resources/models/bpb-topic-modeling'
        model_nexus_name = 'lda_wraped.gensim'  # 'lda_model_mal'
        text_handler = TextHandler('DE')
        pickle_repository = PickelRepository(model_path_conf)
        print(pickle_repository)
        data_matrix = DataMatrix(pickle_repository)
        prediction_model = LDAModel(model_path, model_nexus_name)
        xgboost = Xgboost(model_path_conf)
        vector_handler = VectorHandler(prediction_model, pickle_repository, xgboost)
        nlp = text_handler._nlp
        print(nlp)
        topic_model = PredictionProcessClass(text_handler=text_handler, vector_handler=vector_handler
                                             , data_matrix=data_matrix, prediction_model=prediction_model,
                                             model_path=model_path_conf, nlp=nlp)'''

        logging.basicConfig(level=logging.INFO)
        app_config = YamlConfig.load('.//resources/application.yml')
        model_setup = ModelSetup(app_config)
        topic_model = model_setup.creat_topic_model()

        mongodb = MongoDB(app_config['mongodb'])
        mongodb.connect()

        repository = DetectionResultRepository(mongodb, app_config['modell']['collection'])

        detection_listener = TopicRabbitListener(topic_model, repository, app_config['modell']['project_id'], siemens_services = app_config['service']['siemens_services'])
        return detection_listener


        ''' app_config = YamlConfig.load('.//resources/application.yml')#'.//resources/application.yml')
        model_path = '/topic_modeling/resources/models/bpb-topic-modeling'
        nlp = TextPreprocessing.load_language_model('de_core_news_md')
        text_handler = TextHandler(nlp)
        pickle_repository = PickelRepository(model_path)
        data_matrix = DataMatrix(pickle_repository)
        prediction_model = LDAModel(model_path)
        xgboost = Xgboost(model_path)
        #mongodb = DetectionResultRepository(app_config['mongo'])
        mongodb = MongoDB(app_config['mongo'])
        mongodb.connect()

        repository = DetectionResultRepository(mongodb, 'topic_modeling_collection')'''

        #rabbitmq = RabbitManager(app_config['rabbitmq'], app_name="topic-modelling-service")


        #rabbitmq.register(detection_listener)


        # repository = DetectionResultRepository(mongodb, 'topic_modeling_collection')

        '''vector_handler = VectorHandler(prediction_model, pickle_repository, xgboost)
        topic_model = PredictionProcessClass(text_handler=text_handler, vector_handler=vector_handler
                                      , data_matrix=data_matrix, prediction_model=prediction_model, nlp=nlp,
                                      model_path=model_path)

        detection_listener = TopicRabbitListener(topic_model, repository)'''

        #  rabbitmq = RabbitMQ(app_config['rabbitmq'])
        #rabbit_service = TopicRabbitListener(url=rabbitmq.amqp_url, service=topic_model, mongodb=repository)

        '''return detection_listener'''




class BodyTest:

    def __init__(self, id, pages: list, project_id, document_id, uploaded_time):
        self.pages = pages
        self.project_id = project_id
        self.document_id = document_id
        self.uploaded_time = uploaded_time
        self.id = id

class PageTest:

    def __init__(self, id: str, html: str):
        self.html = html
        self.id = id

class PageTest2:

    def __init__(self, id: str,  html: str):
        self.html = html
        self.id = id

