import ldap
l = ldap.initialize("ldap://ldap.forumsys.com")
out = l.simple_bind("ou=scientists,dc=example,dc=com", "password")
s = l.search_s("ou=scientists,dc=example,dc=com", ldap.SCOPE_SUBTREE, '(objectClass=groupOfUniqueNames)')
for dn, entry in s: 
    print 'Processing', repr(dn)
    print entry
exit()