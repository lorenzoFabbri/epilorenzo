# Hardcover API integration for Quarto
# Fetches currently reading books and displays them

library(httr)
library(jsonlite)

#' Fetch currently reading books from Hardcover API
#'
#' @param api_token Your Hardcover API token from https://hardcover.app/account/api
#' @param user_id Your Hardcover user ID
#' @return A data frame with book information
get_currently_reading <- function(api_token, user_id) {
    # GraphQL endpoint
    endpoint <- "https://api.hardcover.app/v1/graphql"

    # GraphQL query for currently reading books (status_id = 2)
    query <- sprintf(
        '{
    user_books(
      where: {
        user_id: {_eq: %s},
        status_id: {_eq: 2}
      }
    ) {
      book {
        title
        pages
        release_date
        image {
          url
        }
        contributions {
          author {
            name
          }
        }
      }
    }
  }',
        user_id
    )

    # Make the API request
    response <- POST(
        endpoint,
        add_headers(
            authorization = api_token,
            `Content-Type` = "application/json",
            `User-Agent` = "Quarto Academic Website (epilorenzo)"
        ),
        body = list(query = query),
        encode = "json"
    )

    # Check for errors
    if (status_code(response) != 200) {
        warning(
            "Failed to fetch books from Hardcover API: ",
            status_code(response)
        )
        return(data.frame())
    }

    # Parse response
    content <- content(response, as = "parsed")

    if (
        is.null(content$data$user_books) || length(content$data$user_books) == 0
    ) {
        return(data.frame())
    }

    # Extract book information
    books <- lapply(content$data$user_books, function(ub) {
        book <- ub$book
        authors <- sapply(book$contributions, function(c) c$author$name)

        data.frame(
            title = book$title %||% "Unknown",
            author = paste(authors, collapse = ", "),
            pages = book$pages %||% NA,
            release_date = book$release_date %||% NA,
            image_url = book$image$url %||% "",
            stringsAsFactors = FALSE
        )
    })

    do.call(rbind, books)
}

#' Display currently reading books as HTML
#'
#' @param books Data frame from get_currently_reading()
#' @return HTML string
display_books_html <- function(books) {
    if (nrow(books) == 0) {
        return('<p><em>Not currently reading anything.</em></p>')
    }

    html_parts <- lapply(seq_len(nrow(books)), function(i) {
        book <- books[i, ]

        # Build author and metadata info
        metadata <- book$author
        if (!is.na(book$pages)) {
            metadata <- paste0(metadata, " • ", book$pages, " pages")
        }

        # Use CSS classes for layout
        sprintf(
            '<div class="hardcover-book-card">
      %s
      <div class="meta">
        <div class="title">%s</div>
        <div class="author">%s</div>
      </div>
    </div>',
            if (nchar(book$image_url) > 0) {
                sprintf(
                    '<img src="%s" alt="%s">',
                    book$image_url,
                    book$title
                )
            } else {
                '<div class="no-cover">No cover</div>'
            },
            book$title,
            metadata
        )
    })

    paste0(
        '<div class="hardcover-books-row">',
        paste(html_parts, collapse = "\n"),
        '</div>'
    )
}

# Helper function for NULL coalescing
`%||%` <- function(x, y) if (is.null(x)) y else x
