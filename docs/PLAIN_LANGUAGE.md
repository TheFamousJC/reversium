# Reversium, explained without technical background

Living explanation. Last updated: 2026-10-15.

## What it does today

Reversium helps you understand a software package. You give it a ZIP file, and it makes a list of what is inside. For selected kinds of readable code, it identifies named building blocks, references to other software and possible web addresses or application routes.

It presents a report and a diagram. Each finding includes the file and line where it was found, so someone can check the evidence. The diagram connects files to software names they mention. It does not prove that those connections are used when the program runs.

## How to use it

Install Python 3.10 or newer, open a terminal in the Reversium folder and run `python -m reversium`. A browser page opens. Choose your ZIP and click Analyze archive. To create saved reports directly, run `python -m reversium your-package.zip --output reports/my-project`.

## Privacy and cost

The work happens on your computer. There are no subscriptions, accounts or paid AI requests. You still supply the computer, electricity and time. Reports may reveal private file names and software details, so check them before sharing.

## What the report cannot promise

A list of ingredients is not the same as understanding every recipe. Reversium cannot yet explain every business rule, recreate an application automatically or promise a reliable rebuilding price. Some findings are educated pattern matches; the report labels them as such. Missing findings do not prove a feature is absent.

It currently lists compiled programs but does not open them with a decompiler or run them. It does not unpack packages hidden inside the first ZIP. Large or unsupported files may be listed without their contents being inspected.

## What comes next

First we improve understanding of readable code. Then we add tools that inspect compiled software, where some original details have been lost. Later, optional local AI can help draft explanations, and adjustable planning tools can estimate rebuilding work and running costs. Those estimates will show the assumptions behind them.

## Keeping this explanation current

Whenever a feature becomes available, update what the tool does today and remove any promise it still cannot meet. Keep planned capabilities separate from working capabilities.
