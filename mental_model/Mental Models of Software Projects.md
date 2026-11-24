# Mental Models of Software Projects

The notion of **mental model** for software projects is related to Naur's view of *programming as theory building*
(*Programming as Theory Building* [pdf](https://pages.cs.wisc.edu/~remzi/Naur.pdf), [md](https://gist.github.com/onlurking/fc5c81d18cfce9ff81bc968a7f342fb1); Microprocessing and Microprogramming 15 (1985) 253-261).

The main idea introduced by Naur is that the output of the programming activity is mainly a theory that developers construct about the domain in which the software operates.

Naur argues that programming is not mainly the production of code and documents. It is a team building up a *theory* of how part of the world is to be handled by a program. He adapts the concept of "theory" from Gilbert Ryle's work: knowledge that lets you do something intelligently and also *explain* it, *justify* it and *answer questions about it*. 

Naur cites evidence from two cases. 
1. In the first, group B extended a compiler written by group A. B had the full source code, extensive design documents and access to team A, and still proposed patches that "effectively destroyed the power and simplicity" of the system. Group A spotted these instantly, because they could see facilities already built into the structure that B could not see, even though the documentation discussed them. 
2. In the second case, the programmers of a 200,000-line real-time system could find faults using only their own knowledge and the source code. Other teams, given complete documentation, kept running into problems the original team cleared up easily. 

Naur concludes that the theory "could not conceivably be expressed, but is inextricably bound to human beings." A program is *alive* while a team holding its theory controls it. It *dies* when that team is dissolved, even if the program keeps running. Reviving it "merely from the documentation, is strictly impossible."


### What the Theory Lets Programmers do that Text Cannot

Naur relates three capabilities to theory:

1. *Relate the program to the world*: say which part of the world each part of the code corresponds to, and decide what is relevant. 
2. *Justify the design*: explain why each part is the way it is. The basis of that explanation is the programmer's "direct, intuitive knowledge."
3. *Respond to change*: see how a new demand resembles something the program already does, so the change extends the design instead of patching it. 

All three capabilities depend on noticing similarities between real situations. Naur claims that such similarities cannot be written as rules, just as you cannot write rules for recognizing a face or a tune. 

> **NOTE**: The advent of "system 1" like capabilities in AI makes Naur's claim less convincing. The identification of the notion of *theory* as the key product of software development remains a contribution: "owning" a software project means you can explain the program relation to the domain (in the world), justify the design and adapt the program to new conditions or changing requirements.


### Git Example

[Git Mental Model.md](Git%20Mental%20Model.md) provides a concrete illustration of the notion of "theory". One kind of user knows the commands: `add`, `commit`, `checkout -b`, `merge`. Another holds the model behind them: the history is a stream of snapshots, objects are stored by the hash of their content, Git only adds data, files move between three states, and a branch is just a pointer to a commit. The second user can *derive* behavior they have never memorized and deal with complex configurations. Branching is cheap because it creates one pointer. A fast-forward happens when the target commit is a descendant of the current one, so the pointer can simply move. A "lost" commit is usually recoverable because nothing was erased. A merge conflict means both branches changed the same region relative to a common ancestor. 

The first user is like Naur's group B: they have the full documentation (the porcelain commands) and still get stuck the moment something unexpected happens. A software project is the same, except the team has to *build* the model first instead of reading it from a book. Code, specs, architecture and design all come out of that shared understanding of the domain. Writing them is how the team builds the model, not the goal itself.

### Theory versus Specs 

A spec is a finite, explicit set of statements about *what* the system must do: requirements, scenarios, interfaces, constraints. In Naur's terms it is a set of rules and criteria, which is exactly the form he says a theory cannot be reduced to. The spec is one *output* of the theory, a snapshot taken at one moment. The theory is what produced the spec and what will produce the next one, while keeping the project coherent and consistent. 

It is why these requirements were chosen and not others, which parts of the domain were judged irrelevant, which requirements are central and which are incidental, and where the design can stretch when the world changes. 

Two teams can share an identical spec and hold different theories, and they will answer the next change request in incompatible ways. 

## Theory, Domain-Driven Design and Ubiquitous Language

Naur identifies what programming produces: a theory, held by the team, of how the program handles part of the world. Domain-Driven Design (DDD, Eric Evans, *Domain-Driven Design*, 2003) offers *practices* for building that theory on purpose, sharing it across the team, and keeping the code in line with it.

### Domain Model as Written-down Theory

For Evans, a *domain model* is a deliberately selective abstraction of what the team knows about the domain. It is not a diagram or a document; it is the shared understanding the diagrams point to. This is Naur's position, with documentation as a secondary product. Evans calls the work of building the model *knowledge crunching*: developers and domain experts repeatedly work through examples, find gaps and rebuild the model. This is theory building as a team activity together with domain experts.

### Naur's three Capabilities Map onto DDD Practices

| Naur: holding the theory lets you… | DDD practice that supports it |
|---|---|
| Relate the program to the world, and decide what is relevant | *Model-driven design*: code structure mirrors the model, so each class or module corresponds to a domain concept. The model's selectivity is the relevance decision made explicit. |
| Justify why each part is the way it is | Design choices are argued in domain terms ("a Leg belongs to an Itinerary because…"), not in technical terms. |
| Respond to change by extending instead of patching | *Refactoring toward deeper insight*: when a new requirement doesn't fit, the model is revised instead of a special case being bolted on. |


### Ubiquitous Language is the Shared Visible Part of the Theory 

In DDD, the *Ubiquitous Language* is a single vocabulary used consistently everywhere: in conversations with domain experts, in specs, in tests and in identifiers in the code. 

A vocabulary is not a theory: knowing the words `commit`, `ref` and `HEAD` does not let you predict a fast-forward. But the language does three jobs that bear directly on Naur's concerns:
1. *Transmission*: Naur notes that theory spreads only through close work with people who already hold it. Using precise language constantly in conversation helps establish this type of close work. Newcomers absorb the theory by being corrected when they misuse a term.
2. *Detecting drift*: when a domain expert says "that sentence makes no sense", or a change request can't be phrased naturally in the language, the theory has been exposed and tested. Awkward phrasing is an early warning that a change would be a patch, not an extension, which is the decay Naur describes.
3. *Binding code to theory*: when names in the code are the domain's terms, Naur's first capability (mapping text to the world) is partly built into the code itself.

For example, the [Git Mental Model](Git%20Mental%20Model.md) defines Git's ubiquitous language: blob, tree, commit, ref, HEAD, index, working tree. Each term has a precise meaning, and together they make up the basis of the theory. 

### Bounded Contexts Make Clear that a Theory Belongs to a Team

In DDD, a model and its language hold only inside a *Bounded Context*. The same word ("Customer", "Order") can mean different things in billing and in shipping, and each context is usually owned by one team. This matches Naur's claim that a theory is tied to the people who hold it. 

A Bounded Context is the scope of one team's theory, and a *Context Map* describes how the theories of different teams relate. 

### Where Naur and DDD Differ

- *Can the theory be expressed?* Naur says it fundamentally cannot. DDD is more optimistic: much of it can be made explicit in the model, the language and the code. Some judgment is always left over, such as which similarities matter or when to reshape the model, but DDD tries to keep that leftover small. The note above on "system 1"-like AI leans the same way as DDD.
- *Method.* Naur argues that "for the primary activity of the programming there can be no right method." DDD is a set of patterns and principles, not an ordered procedure. Naur explicitly accepts such things as aids that improve the theory, as long as the programmer decides when to use them. 


## Why Theory, Domain Models and Mental Models Matter with AI Agents

The ubiquitous language is the cheapest part of the theory to hand to an LLM. 
A glossary of domain terms can go in the agent's instructions, specs can be required to use those terms (as the OpenSpec capability names `issue-enrichment` and `issue-routing` do in the triage example), and generated code that brings in synonyms or new concepts can be rejected. 

That lets the agent work *inside* the team's theory. It still leaves the team responsible for what the language cannot hold: deciding what is relevant and when the model itself has to change. 
It points to responsibility that the human team must take to control the behavior of AI agents: preserve the code integrity with respect to theory and maintain shared understanding.


