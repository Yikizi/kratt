### Instructions for Writing a Thesis Using the LaTeX Template

This guide will help you navigate and use the LaTeX template for your thesis, which is designed for students at Tallinn University of Technology (TalTech). Follow the instructions below to customize and structure your thesis correctly.

---

### 1. **Getting Started**

#### Files Structure:
- **`main.tex`**: This is the main file where you will compile the document.
- **`thesis.sty`**: This file contains the formatting and style settings for your thesis. You shouldn't change there anything.
- **`config.tex`**: Contains variables for the thesis.
- **`chapters` folder**: Contains individual chapter files.
- **`appendices` folder**: Contains the appendices for your thesis.
- **`misc` folder**: Miscellaneous files for title pages, declarations, and the license.
- **`figures` folder**: Contains the figures for your thesis.


You should only compile the `main.tex` file, as all the content and formatting is linked to this file.

---

### 2. **Customizing Your Thesis**

Several fields in the `config.tex` file need to be filled out with your information. These commands are critical for generating the title page and metadata for your document.

#### Important Fields to Define:
1. **Language Selection** (`\lang`): Choose either Estonian (`EST`) or English (`ENG`) for your thesis.
   ```latex
   \newcommand{\lang}{EST} % or ENG
   ```
   Note that default language of this template is Estonian.

2. **Thesis Title**:
   - In Estonian (`\thesisTitleEst`)
   - In English (`\thesisTitleEng`)
   ```latex
   \newcommand{\thesisTitleEng}{Thesis Title in English}
   \newcommand{\thesisTitleEst}{Lõputöö pealkiri eesti keeles}
   ```

3. **Thesis Type**: Define whether it is a Bachelor's or Master's thesis.
   ```latex
   \newcommand{\thesisType}{Bachelor's Thesis} % or Master's Thesis
   ```

4. **Author Details**:
   - Your name and student code
   ```latex
   \newcommand{\authorName}{Your Name}
   \newcommand{\studentcode}{Your Student Code}
   ```

5. **Supervisor Details**:
   - Name and academic degree of the main supervisor and co-supervisor (if applicable)
   ```latex
   \newcommand{\supervisorName}{Supervisor's Name}
   \newcommand{\supervisortitle}{Supervisor's Academic Degree}
   ```

6. **Publication Year and Signature Date**: These are automatically set to the current year and date, but you can hard-code it if needed.
   ```latex
   \newcommand{\Year}{The Year}
   \newcommand{\signatureDate}{The Date}
   ```

---

### 3. **Writing the Abstracts**

The template automatically arranges abstracts in Estonian and English, depending on the main language you selected (Estonian-first if your thesis is in Estonian, and vice versa).

Just write the main content of each abstract, and the template will auto-generate details like page count, chapters, figures, and tables. For example:

"The thesis is in Estonian and contains 5 pages of text, 4 chapters, 1 figure, and 1 table."

---

### 4. **Writing the Chapters**

All chapter content should be placed inside the **`chapters`** folder. You can edit or create new `.tex` files for each chapter. The main file to include all chapters is `chapters_main.tex`.

Example of including chapters:
```latex
\chapter{Introduction}\label{chapter:introduction}
\input{chapters/introduction.tex}     % Introduction chapter
\chapter{Methodology}\label{chapter:methodology}
\input{chapters/methodology.tex} % Methodology chapter
```

You can find more examples by looking at the **`chapters_main.tex`** file.

If you need to add appendices, it’s a bit more complicated. Check the **`appendices_main.tex`** file for guidance on how to do this.

---

### 5. **Using Labels and Referencing Chapters**

Use `\label{key}` to define a label and `\ref{key}` to reference it in your text. For chapters, label them as `\label{chapter:key}` and reference with `Chapter \ref{chapter:key}`. For sections, use `\label{section:key}` and reference with `Section \ref{section:key}`.

When dividing a part into multiple chapter, you can use labels like `\label{chapter:key-subpart}` for each chapter. Reference them as `Chapter \ref{chapter:key-subpart}`. 

Example for chapters:
```latex
\chapter{Introduction}\label{chapter:introduction}
```
Reference:
```latex
As discussed in Chapter \ref{chapter:introduction}, ...
```

For dividing a part into two chapters:
```latex
\chapter{Analysis}\label{chapter:discussion-analysis}
\chapter{Conclusions}\label{chapter:discussion-conclusions}
```
Reference:
```latex
In Chapter \ref{chapter:discussion-analysis}, we analyzed the data. In Chapter \ref{chapter:discussion-conclusions}, we discuss the results further.
```
---

### 6. **List of Figures and Tables**

The template automatically generates lists of figures and tables if figures or tables are present in your document. These will appear after the Table of Contents.

If your thesis doesn’t include any figures or tables, open `chapters/misc_main.tex` and remove the code block for the List of Figures or List of Tables.

To include a figure or table:
```latex
\begin{figure}[h!]
    \centering
    \includegraphics[width=0.8\textwidth]{figures/sample_figure.png}
    \caption{Description of the figure}
    \label{fig:sample}
\end{figure}

\begin{table}[h!]
    \centering
    \begin{tabular}{|c|c|}
        \hline
        Column 1 & Column 2 \\
        \hline
    \end{tabular}
    \caption{Description of the table}
    \label{tab:sample}
\end{table}
```

For additional examples, check the file `chapters/introduction.tex`.

---

### 7. **Bibliography**

The bibliography is added automatically at the end of the thesis. 

1. **Fill the `references.bib` file**:
   - Add your references in `references.bib`, using the BibTeX format:

     ```bibtex
     @misc{example-reference,
         author = "L. Masinter",
         title = "Hyper Text Coffee Pot Control Protocol (HTCPCP/1.0)",
         url = "https://tools.ietf.org/html/rfc2324",
         note = "[Accessed: 24-05-2019]"
     }
     ```
2. **Common Entry Types in BibTeX/BibLaTeX**:
   Each entry type has a specific purpose and structure. Below are some commonly used entry types:

   - **`@article`** is used for journal publications, focusing on details like volume, issue, and pages.
     ```bibtex
     @article{smith2024,
       author = {John Smith},
       title = {Title of the article},
       journal = {Journal Name},
       year = {2024},
       volume = {12},
       number = {4},
       pages = {123-145}
     }
     ```

   - **`@book`** is for standalone books, typically with a publisher and place of publication.
     ```bibtex
     @book{doe2020,
       author = {Jane Doe},
       title = {Title of the Book},
       publisher = {Publisher Name},
       year = {2020},
       address = {City, Country}
     }
     ```

   - **`@inproceedings`** is specific to conference proceedings and includes conference-specific details.
     ```bibtex
     @inproceedings{lee2019,
       author = {Lee Chen},
       title = {Conference Paper Title},
       booktitle = {Proceedings of Conference},
       year = {2019},
       pages = {102-115},
       organization = {Conference Organization}
     }
     ```

   - **`@misc`** offers flexibility for non-standard references without defined fields.
     ```bibtex
     @misc{website2023,
       author = {Author Name},
       title = {Website Title},
       url = {https://website.example},
       note = {Accessed: 2024-01-01}
     }
     ```

3. **Cite references within the text**:
   - Use `\cite{key}` to cite a reference within your text, where `key` matches the identifier in your `.bib` file (e.g., `\cite{website2023}`).


---

### 8. **Compilation**

After filling in your details and content, compile the `main.tex` file using a LaTeX editor (such as Overleaf, TeXShop, or TeXworks). Ensure that all referenced files (figures, chapters, appendices, etc.) are correctly linked and that there are no missing files or errors.

---

### 9. **Final Checklist**

- Title page correctly filled out in your chosen language.
- All chapters included and formatted.
- All appendices included and listed in the Table of Contents.
- Figures and tables properly inserted and referenced.
- Bibliography included and correctly formatted.
- The document compiles without errors.
