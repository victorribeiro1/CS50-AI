import os
import random
import re
import sys

# Control constants
DAMPING = 0.85
SAMPLES = 10000

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    
    # Crawl and extract links from the provided corpus
    corpus = crawl(sys.argv[1])

    # Calculate PageRank using sampling
    ranks = samplePageRank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")

    # Calculate PageRank using iteration
    ranks = iteratePageRank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")

def crawl(directory):
    """
    Analyze a directory of HTML pages and extract links to other pages.
    Returns a dictionary where each key is a page, and values are
    sets of all other pages in the corpus linked by that page.
    """
    pages = dict()

    # Iterate through each HTML file in the directory
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            # Find all links in each HTML page
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            # Remove self-links (if any)
            pages[filename] = set(links) - {filename}

    # Filter to include only valid links within the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages

def transitionModel(corpus, page, dampingFactor):
    """
    Returns a probability distribution over which page to visit next,
    given the current page. With probability `dampingFactor`, choose a
    random link linked by the page. With probability `1 - dampingFactor`,
    choose randomly from all pages in the corpus.
    """

    # Initialize probability distribution
    propDist = {}

    totalPages = len(corpus.keys())
    outgoingLinks = len(corpus[page])

    if outgoingLinks < 1:
        # If no links, distribute evenly among all pages
        for key in corpus.keys():
            propDist[key] = 1 / totalPages
    else:
        # If there are links, distribute based on damping factor
        randomFactor = (1 - dampingFactor) / totalPages
        linkFactor = dampingFactor / outgoingLinks

        for key in corpus.keys():
            if key not in corpus[page]:
                propDist[key] = randomFactor
            else:
                propDist[key] = linkFactor + randomFactor

    return propDist

def samplePageRank(corpus, dampingFactor, n):
    """
    Returns PageRank values for each page by sampling `n` pages,
    based on the transition model, starting with a random page.

    Returns a dictionary where the keys are page names, and the values are
    their estimated PageRank (values between 0 and 1). All PageRank values sum to 1.
    """

    # Initialize sample counts to zero
    samplesDict = corpus.copy()
    for i in samplesDict:
        samplesDict[i] = 0

    sample = None

    # Perform `n` samples
    for _ in range(n):
        if sample:
            # Choose next page based on the transition model
            dist = transitionModel(corpus, sample, dampingFactor)
            distList = list(dist.keys())
            distWeights = [dist[i] for i in dist]
            sample = random.choices(distList, distWeights, k=1)[0]
        else:
            # For the first sample, choose a random page
            sample = random.choice(list(corpus.keys()))

        # Increment the count for the sampled page
        samplesDict[sample] += 1

    # Convert sample counts to probabilities
    for item in samplesDict:
        samplesDict[item] /= n

    return samplesDict

def iteratePageRank(corpus, dampingFactor):
    """
    Returns PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Returns a dictionary where keys are page names and values are
    their estimated PageRank. All values sum to 1.
    """

    totalPages = len(corpus)
    oldRanks = {}
    newRanks = {}

    # Initialize each page with a rank of 1/n
    for page in corpus:
        oldRanks[page] = 1 / totalPages

    # Iterate until PageRank values stabilize (convergence)
    while True:
        for page in corpus:
            tempRank = 0
            for linkingPage in corpus:
                # Check if the current page is linked by linkingPage
                if page in corpus[linkingPage]:
                    tempRank += (oldRanks[linkingPage] / len(corpus[linkingPage]))
                # If a page has no links, distribute uniformly to all pages
                if len(corpus[linkingPage]) == 0:
                    tempRank += (oldRanks[linkingPage]) / len(corpus)

            # Apply damping factor and calculate the new rank
            tempRank *= dampingFactor
            tempRank += (1 - dampingFactor) / totalPages
            newRanks[page] = tempRank

        # Check if the maximum change in PageRank values is less than the threshold
        difference = max([abs(newRanks[x] - oldRanks[x]) for x in oldRanks])
        if difference < 0.001:
            break
        else:
            oldRanks = newRanks.copy()

    return oldRanks

if __name__ == "__main__":
    main()