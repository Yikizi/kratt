function createKrattPilotFeedbackForm() {
  const form = FormApp.create("Kratt kasutajatesti tagasiside");
  form.setDescription(
    "TalTechi bakalaureusetöö kasutajatest. Vastused salvestatakse pseudonüümse osaleja ID-ga. Ära sisesta nime ega muid otseseid isikuandmeid. " +
    "Kratt juhib selles demos ühte WiZ lampi ning oskab kõrvalt kellaaega, kuupäeva, ilma ja lühikesi üldküsimusi abimudeli kaudu. " +
    "Proovi toetatud piire: värvid, heledus, efektid, tule olek, homne ilm teises linnas või poolik käsk nagu \"pane tuli teist värvi\". " +
    "Taimerid, muusika, uksed ja muud seadmed ei ole selle demo võimekused."
  );
  form.setCollectEmail(false);
  form.setLimitOneResponsePerUser(false);
  form.setAllowResponseEdits(false);
  form.setProgressBar(true);

  form.addTextItem()
    .setTitle("participant_id")
    .setHelpText("Sama ID, mida kasutatakse salvestussessioonis, nt P01. Ära sisesta nime.")
    .setRequired(true);

  form.addTextItem()
    .setTitle("session_id")
    .setHelpText('Kopeeri session.json või operaatori lehelt. Kui seda veel ei tea, kirjuta "unknown".')
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle("consent_level")
    .setChoiceValues(["metrics only", "audio opt-in"])
    .setRequired(true);

  form.addPageBreakItem().setTitle("Taust");

  form.addMultipleChoiceItem()
    .setTitle("Eesti keele tase")
    .setChoiceValues(["emakeel", "C1-C2", "B1-B2", "A1-A2", "muu", "ei soovi öelda"])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle("Varasem häälassistendi kasutus")
    .setChoiceValues(["mitte kunagi", "harva", "iganädalaselt", "iga päev"])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle("Nutikodu kasutus")
    .setChoiceValues(["ei kasuta", "aeg-ajalt", "regulaarselt"])
    .setRequired(true);

  form.addPageBreakItem().setTitle("UMUX-Lite");

  form.addScaleItem()
    .setTitle("Selle süsteemi võimekused vastavad mu nõudmistele.")
    .setBounds(1, 7)
    .setLabels("ei nõustu üldse", "nõustun täielikult")
    .setRequired(true);

  form.addScaleItem()
    .setTitle("Seda süsteemi on lihtne kasutada.")
    .setBounds(1, 7)
    .setLabels("ei nõustu üldse", "nõustun täielikult")
    .setRequired(true);

  form.addPageBreakItem().setTitle("Ülesande lihtsus");

  form.addScaleItem()
    .setTitle("Kui lihtne oli Kratiga etteantud ülesandeid lõpule viia?")
    .setBounds(1, 7)
    .setLabels("väga raske", "väga lihtne")
    .setRequired(true);

  form.addPageBreakItem().setTitle("Kratt-spetsiifiline tagasiside");

  form.addScaleItem()
    .setTitle("Süsteem reageeris piisavalt usaldusväärselt.")
    .setBounds(1, 5)
    .setLabels("üldse ei nõustu", "nõustun täielikult")
    .setRequired(true);

  form.addScaleItem()
    .setTitle("Süsteem reageeris piisavalt kiiresti.")
    .setBounds(1, 5)
    .setLabels("üldse ei nõustu", "nõustun täielikult")
    .setRequired(true);

  form.addScaleItem()
    .setTitle("Käskude sõnastamine tundus loomulik.")
    .setBounds(1, 5)
    .setLabels("üldse ei nõustu", "nõustun täielikult")
    .setRequired(true);

  form.addScaleItem()
    .setTitle("Kasutaksin sellist süsteemi kodus.")
    .setBounds(1, 5)
    .setLabels("üldse ei nõustu", "nõustun täielikult")
    .setRequired(true);

  form.addPageBreakItem().setTitle("Avatud tagasiside");

  form.addParagraphTextItem()
    .setTitle("Mis oli kõige häirivam või üllatavam?")
    .setRequired(false);

  Logger.log("Edit URL: " + form.getEditUrl());
  Logger.log("Public URL: " + form.getPublishedUrl());
}
