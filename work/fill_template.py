import zipfile, os, re, shutil
from lxml import etree
src = r'C:\Users\seree\Downloads\conference-template-a4 (1).docx'
out = r'C:\Users\seree\Documents\Codex\2026-10-09\schedule-aware-fault-diagnosis-for-urban\outputs\schedule_aware_irrigation_fault_diagnosis.docx'
tmp = out + '.tmp'
repl = {
0: 'Schedule-Aware Machine Learning for Fault Diagnosis in Urban Irrigation Networks',
1: '[Student names and affiliations to be added]',
4: '[Group member names]  |  CSIT305 Emerging Technology Research and Innovation Project  |  University of Wollongong in Dubai  |  Dubai, UAE',
10: 'Abstract—Urban irrigation readings change with planned watering, while pipe leaks and clogged emitters can produce overlapping flow and pressure anomalies. This paper proposes a simulation-based study of a machine-learning classifier that distinguishes normal scheduled operation, pipe leaks, and clogged emitters or sprinkler heads. A digital twin will generate labelled scenarios for a small zoned network; the classifier will use schedule context and simulated hydraulic measurements. It will be compared with a schedule-aware threshold alert on held-out watering schedules and fault combinations. Evaluation will report per-class precision and recall, macro F1, missed-fault rate, false-alert rate, and failure cases. The expected contribution is a reproducible assessment of whether schedule context improves fault-type diagnosis over anomaly alerts under defined synthetic conditions. No performance result is claimed before the experiments are conducted. Synthetic scenarios support controlled testing but cannot establish performance in operational municipal networks.',
11: 'Index Terms—urban irrigation, fault diagnosis, machine learning, digital twin, synthetic data, leak detection, emitter clogging.',
12: 'I. INTRODUCTION',
13: 'Urban irrigation systems maintain parks, street trees, and landscaped public spaces. Their sensors may report flow and pressure changes when scheduled zones open or close. The same measurements may also change when a pipe leaks or an emitter or sprinkler head becomes clogged. A threshold alert can flag an unusual value, but it may not tell maintenance staff which condition is most likely. This matters because a suspected leak calls for pipe inspection, while a suspected clog calls for inspection of a delivery point or zone.\n\nMachine learning (ML) offers a way to classify patterns across multiple readings, while a digital twin provides a controlled representation of the network for testing. The main technology investigated here is ML-based diagnosis; the supporting technology is a hydraulic digital twin that generates scenarios with known labels. The research question is: Can an ML model using schedule context and digital-twin flow and pressure data distinguish leaks, clogged emitters or sprinkler heads, and normal scheduled operation more effectively than a threshold-based alert on unseen simulated schedules and fault scenarios?\n\nThe study is scoped to a small, simulated, zoned network. It does not claim to repair faults, localize them precisely, or establish field readiness. Its contribution will be an evaluated comparison, a documented scenario design, and a prototype display that turns a detected pattern into a cautious inspection suggestion.',
14: 'II. RELATED WORK',
15: 'A. Leak Detection and Scheduled Events',
16: 'Zhang et al. developed a convolutional-neural-network workflow for acoustic files in Adelaide’s smart water network. Their system first identified anomalies and then used a Siamese model to distinguish scheduled events, including irrigation near parks, from other anomalies; the reported validation used real network recordings [1]. This work demonstrates that schedule context can prevent some legitimate events from being treated as faults. Its sensor modality and water-distribution setting differ from this project’s simulated flow-and-pressure measurements in a landscape irrigation network.',
17: 'B. Emitter-Clogging Detection',
18: 'Petit et al. review laboratory, field, and sensor approaches to drip-emitter clogging. They describe hydraulic measurements as indirect indicators and discuss the difficulty of directly detecting clogging in the field [2]. This supports treating clog diagnosis as a distinct maintenance problem rather than assuming every abnormal reading indicates a leak. The review focuses on drip irrigation and does not evaluate joint classification of scheduled operation, leaks, and clogs in an urban landscape network.',
19: 'III. GAP AND RESEARCH QUESTION',
20: 'The two sources cover complementary parts of the problem: schedule-aware leak/anomaly classification in a municipal water network [1] and methods for assessing emitter clogging [2]. They do not by themselves establish that the combined question has never been studied. The defensible project gap is therefore a focused application question: whether schedule context and simulated hydraulic patterns can support three-way diagnosis in one small urban-irrigation model, and how that compares with a threshold alert. A broader literature review is required before making a novelty claim.',
21: 'Research question: Can a machine-learning model using flow, pressure, and watering-schedule context distinguish pipe leaks, clogged emitters or sprinkler heads, and normal scheduled operation more effectively than a threshold-based alert on held-out simulated schedules and fault scenarios? The contribution will be validated evidence under specified simulated conditions, not simply the existence of a dashboard or classifier.',
22: 'IV. PROPOSED METHOD',
23: 'A controlled simulation and comparative evaluation will be used. The twin will represent a small network with a source or pump, a main pipe, branches, zone valves, and irrigation outlets. An EPANET-compatible hydraulic simulator (for example, WNTR) can generate flow and pressure time series from a network configuration. The team should record the simulator version, parameters, random seeds, and configuration files so another group can reproduce the scenarios. The model will receive timestamped flow and pressure features together with the planned valve/zone schedule; actual sensor hardware is outside the present scope.',
24: 'A. Scenario and Synthetic-Data Design',
25: 'Normal cases will include scheduled zone starts, stops, and changes in the order or duration of watering. Fault cases will introduce leaks at different pipe segments and clogging at selected outlets or zones, with multiple severity levels. The class label will be normal, leak, or clog. Simulation runs will vary demand, initial pressure, and schedule so the model cannot rely on a single fixed trace.',
26: 'For each run, the twin will export time-aligned flow and pressure readings, schedule state, and the known simulated condition. Noise and missing readings may be added at documented levels to test robustness. These are synthetic measurements: they allow controlled labels and repeatable fault injection, but their patterns depend on model assumptions and may omit soil, weather, aging, sensor drift, installation variation, and real operator behavior.',
27: 'Data will be split by complete simulation runs, not by randomly shuffling adjacent time windows. A subset of watering schedules and fault combinations will be held out until final evaluation. This reduces leakage between similar traces and tests whether the classifier transfers to schedules or combinations it did not see during training.',
28: '',
29: 'The baseline will be a schedule-aware threshold rule calibrated on normal training runs. It will compare observed readings with expected ranges for the active zone and flag departures; its thresholds and tuning procedure will be fixed before test evaluation.',
30: 'B. Classifier and Evaluation',
31: 'A Random Forest classifier is proposed because it is feasible for a small labelled dataset and can use tabular features such as rolling flow/pressure summaries, pressure changes, schedule state, and zone identity. Feature windows and model settings will be selected using training/validation data only. The classifier and threshold baseline will receive the same simulated measurements and schedule context where applicable. The three target classes and the train/validation/test split will be documented before fitting.',
32: 'Evaluation will report the confusion matrix, per-class precision and recall, macro-averaged F1, missed-fault rate, and false-alert rate. Macro F1 prevents the normal class from dominating the headline score if fault examples are less frequent. Results will be broken down by watering schedule, fault severity, and fault location. The primary comparison is performance on held-out runs, not training accuracy.',
33: '',
34: 'Failure analysis will inspect leak-to-clog and fault-to-normal confusion, especially around valve transitions, mild faults, noisy readings, and missing data. The team will record the failure, likely cause, any model or scenario revision, and the retest result. No numerical result is reported in this proposal; values will be inserted only after the planned evaluation is run.',
35: 'C. Prototype Architecture',
36: '1) Schedule and network inputs: network topology, zone schedule, and sensor variables define each simulated run.',
37: '2) Digital twin: the hydraulic simulator produces time-series flow and pressure readings for normal and fault scenarios.',
38: '3) ML diagnosis: a trained classifier returns class probabilities for normal operation, leak, and clog.',
39: '4) Threshold baseline: a fixed schedule-aware rule produces a comparable alert for the same test run.',
40: '5) Prototype display: a simple interface shows the likely condition, confidence, affected zone if available, and a cautious inspection suggestion. Low confidence should be labelled uncertain and should prompt inspection rather than an automatic maintenance action.',
41: '', 42: '', 43: '', 44: '', 45: '', 46: '',
47: 'This pipeline makes the technology integration explicit: the digital twin supplies controlled, labelled evidence; ML learns the classification mapping; and the display presents the result for a human maintenance decision. The project evaluates diagnostic support, not autonomous control of valves or repair instructions.',
48: 'V. RESPONSIBLE DESIGN AND PRACTICAL LIMITS',
49: 'Synthetic data are justified because real municipal sensor records may be unavailable, costly, or sensitive, and known fault labels are difficult to obtain for real networks. Simulation allows repeatable controlled scenarios and supports development before any field use. However, a model trained only on the twin may learn simulator artifacts. Performance must therefore be described as performance within the tested model and scenarios, not as expected real-world accuracy.',
50: 'A. Security, Privacy, and Operations',
51: 'The prototype will use simulated data and will not connect to operational irrigation controls. If future work uses field data, access should be authorized, network and location details minimized where practical, and data protected in storage and transfer. Predictions should remain advisory: a false leak alert can waste inspection effort, while a missed leak or clog can delay maintenance. Human review and a clear uncertainty state reduce the risk of over-relying on an unvalidated model.',
52: '', 53: '', 54: '', 55: '', 56: '', 57: '',
58: 'VI. EXPECTED CONTRIBUTION AND CONCLUSION',
59: 'The project will contribute a reproducible simulation-based evaluation of three-way irrigation diagnosis under changing watering schedules. It will test whether a machine-learning classifier provides more useful fault-type information than a schedule-aware threshold alert, using held-out schedules, fault severities, and fault locations. A small display will demonstrate how the result could guide an initial inspection. The contribution is the evidence and documented method produced by the comparison, not a claim that the prototype has already improved municipal maintenance.',
60: 'The principal limitation is the use of synthetic hydraulic data. The study cannot establish field accuracy, water savings, or reduced maintenance cost. A small network and a limited set of fault models may also underrepresent real equipment variation, weather, soil effects, sensor faults, and simultaneous failures.',
61: 'Future work should validate the approach with authorized field data, compare simulated patterns with measured fault cases, assess sensor placement and uncertainty calibration, and examine whether operators find the alerts useful. Until then, the prototype is a research demonstrator and its outputs require inspection by a qualified maintenance team.',
62: '',63: '',64: '',65: '',66: '',67: '',
68: 'Generative AI Use Declaration',
69: 'Generative AI assisted with drafting and language refinement for this document. The student authors must verify every citation and technical claim, revise the text to reflect their own research and implementation, and accurately declare any additional AI-assisted code, data, or testing in the final submission.',
70: 'REFERENCES',
71: '',72: '',73: '',74: '',75: '',
76: 'C. Zhang, B. J. Alexander, M. L. Stephens, M. F. Lambert, and J. Gong, “A convolutional neural network for pipe crack and leak detection in smart water network,” Structural Health Monitoring, vol. 22, no. 1, pp. 232–244, 2023, doi: 10.1177/14759217221080198.',
77: 'J. Petit, S. Mas García, B. Molle, R. Bendoula, and N. Aït-Mouheb, “Methods for drip irrigation clogging detection, analysis and understanding: State of the art and perspectives,” Agricultural Water Management, vol. 272, Art. no. 107873, 2022, doi: 10.1016/j.agwat.2022.107873.',
78: '',79: '',80: '',81: '',82: '',83: '',84: '',85: '',86: '',87:'',88:'',89:'',90:''
}
with zipfile.ZipFile(src) as zin, zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data=zin.read(item.filename)
        if item.filename=='word/document.xml':
            root=etree.fromstring(data)
            ns={'w':etree.QName(root).namespace}
            paras=root.xpath('.//w:body/w:p',namespaces=ns)
            for i, p in enumerate(paras):
                if i not in repl: continue
                text=repl[i]
                texts=p.xpath('.//w:t',namespaces=ns)
                if not texts and text:
                    r=etree.SubElement(p, '{%s}r'%ns['w']); t=etree.SubElement(r,'{%s}t'%ns['w']); texts=[t]
                if texts:
                    texts[0].text=text
                    if text[:1].isspace() or text[-1:].isspace(): texts[0].set('{http://www.w3.org/XML/1998/namespace}space','preserve')
                    for t in texts[1:]: t.text=''
            # Remove legacy text-box figure containing template guidance, preserving unrelated package parts.
            for p in root.xpath('.//w:body/w:p',namespaces=ns):
                if p.xpath('.//w:txbxContent',namespaces=ns):
                    parent=p.getparent(); parent.remove(p)
            data=etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
        # Convert Strict OOXML namespace URIs to the broadly supported Transitional equivalents in the output copy.
        data=data.replace(b'http://purl.oclc.org/ooxml/wordprocessingml/main',b'http://schemas.openxmlformats.org/wordprocessingml/2006/main')
        data=data.replace(b'http://purl.oclc.org/ooxml/officeDocument/relationships',b'http://schemas.openxmlformats.org/officeDocument/2006/relationships')
        data=data.replace(b'http://purl.oclc.org/ooxml/drawingml/wordprocessingDrawing',b'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing')
        data=data.replace(b'http://purl.oclc.org/ooxml/drawingml/main',b'http://schemas.openxmlformats.org/drawingml/2006/main')
        data=data.replace(b'http://purl.oclc.org/ooxml/drawingml/picture',b'http://schemas.openxmlformats.org/drawingml/2006/picture')
        data=data.replace(b'http://purl.oclc.org/ooxml/officeDocument/customXml',b'http://schemas.openxmlformats.org/officeDocument/2006/customXml')
        zout.writestr(item,data)
os.replace(tmp,out)
print(out)
